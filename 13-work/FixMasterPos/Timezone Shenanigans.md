We have these functions:
```ts
/**
 * Gets the user's timezone-adjusted date based on their IP address.
 * Makes a request to ip-api.com via getUserTimeZone() to get location data
 * and returns a Date object in the user's local timezone.
 *
 * @param request - The Fastify request object containing client IP
 * @returns Promise resolving to a Date object in user's timezone, or current UTC date if error
 */
export async function parseDateString(request: FastifyRequest): Promise<Date> {
  const validDate = await getUserTimeZone(request);
  return validDate;
}

/**
 * Gets the user's timezone and current date/time based on their IP address.
 * Makes a request to ip-api.com to get location data including timezone.
 * Converts the current time to the user's timezone using Luxon.
 * 
 * @param request - The Fastify request object containing client IP
 * @returns Promise resolving to a Date object in user's timezone, or current UTC date if error
 * @throws Error if location data cannot be retrieved or is invalid
 */
export async function getUserTimeZone(request: FastifyRequest): Promise<Date> {
  try {
    const clientIp = requestIp.getClientIp(request);

    const geoResponse = await axios.get(`http://ip-api.com/json/${clientIp}`);
    const locationData = geoResponse.data;

    if (!locationData || locationData.status !== "success") {
      throw new Error("Failed to get location data");
    }

    const userDate = DateTime.now().setZone(locationData.timezone);
    const userDateTime = userDate.toFormat("yyyy-MM-dd HH:mm:ss");
    const userDateObj = parseFormattedDate(userDateTime);

    return userDateObj;
  } catch (error) {
    logger.error(error, "Error fetching user location or time zone:");
    return new Date();
  }
}
```

Wherever a date is required for a user action, this method uses the client IP to get their location and timezone. That date is stored as-is in the DB. If the IP lookup fails, we generate a new Date() - which is UTC.

This is a weird solution because there's no defined timezone used in the DB. We're just storing whatever timezone the user happened to be in when they made the request.
## The Obvious Fix
The solution is: use UTC on backend, and use Luxon on frontend to display time in the user's local timezone. Shikena. 

BUT we **need** to migrate the time currently stored in DB. After migrating, we only need to use new Date().
## The Migration Problem
From what I've seen in the codebase, we just store the timestamp gotten from `parseDateString`, which is the local timezone of the user that made that request.

MongoDB stores dates as 64-bit integers (UTC milliseconds since the Unix epoch), without timezone information. So this is also a problem, as we have no clue what timezone any dates are in.
## Possible Solutions
### Option 1: Try to Guess the Timezone
- Look at each stored date and try to figure out what timezone it was originally in by comparing it to UTC time? I don't think this is possible though.
- Or use US timezone by default since that's where all our customers are and convert back to UTC
### Option 2: Make Users Set Their Timezone
- Add timezone field to user profiles
- Have users set their timezone preference
- Use that to convert their old data
- But this isn't foolproof either, and requires user action, which they likely won't take
- Also how does this work really? Do we take the dates in DB, slap a timezone offset, and convert the timezone with offset to UTC? 
### Option 3: Just Accept the L
- Mark existing data as "timezone unknown"
- Only do UTC properly going forward
- Show old data with some disclaimer
- This is e-commerce, and fucking up the timestamps is a **bad** idea
### Option 4: Mix of Everything
- Start using UTC for new stuff immediately
- Try to migrate old data in the background
- Flag the sketchy conversions
- Also a bad idea methinks, because the frontend will try to use Luxon to convert the dates to local time. If the data sent to it is already in local time, users will see inaccurate time on older items - which will result in complaints.
## Questions
1. How important is it that the old timestamp data is accurate?
2. Do we have any other user data that might help us guess timezones?
3. Should we just implement UTC for new data now and deal with old data separately?
4. For dates where we can't figure out the timezone, should we assume UTC or what?
5. How do we even validate if our migration worked correctly?
## Problem In Original Code
The existing code has a bug which contributes to our current problem, but might actually be intentional. And the fix is a roundabout way to get to the final point - using a UTC date.

The code at the top of this file calls `parseFormattedDate`. Here is the function:
```ts
function parseFormattedDate(dateString: string): Date {
    const regex = /^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/;
    const match = dateString.match(regex);

    if (!match) {
        return new Date();
    }

    const [, year, month, day, hour, minute, second] = match;
    const isoDateString = `${year}-${month}-${day}T${hour}:${minute}:${second}.000Z`;

    const validDate = new Date(isoDateString);

    if (isNaN(validDate.getTime())) {
        return new Date();
    }

    return validDate;
}
```

This function parses the date fetched using the users' IP, strips the timezone offset and saves it in the DB.
Assuming the date fetched is: `2025-06-23T11:27:40.897+01:00`, it would be stored in the DB as: `2025-06-23T11:27:40.000Z`.

Assuming we used Luxon as intended, this problem would not exist, as the dates would be stored as UTC. The code would look like this:
```ts
export async function getUserTimeZone(request: FastifyRequest): Promise<Date> {
  try {
    const clientIp = requestIp.getClientIp(request);

    const geoResponse = await axios.get(`http://ip-api.com/json/${clientIp}`);
    const locationData = geoResponse.data;

    if (!locationData || locationData.status !== "success") {
      throw new Error("Failed to get location data");
    }

    const userDate = DateTime.now().setZone(locationData.timezone);
    return userDate.toJsDate(); // JS dates are in UTC

    return userDateObj;
  } catch (error) {
    logger.error(error, "Error fetching user location or time zone:");
    return new Date();
  }
}
```

But then, like I mentioned earlier, this is a roundabout way of writing this:
```ts
export async function getUserTimeZone(request: FastifyRequest): Promise<Date> {
	return new Date(); // utc
}
```
## Analysing Date Offsets
I needed to test the Date setup, so i created an order using the create order endpoint. I noticed that this endpoint uses `parseDateString` to get the `createdAt` date, while `updatedAt` is populated by MongoDb. This is excellent, cause it allows us to infer a user's timezone by analysing the delta between these fields.

Here's how:
1. **Calculate the delta** between createdAt and updatedAt for records where both exist
2. **Group by common timezone offsets** - there'll likely be patterns like +1 hour, +5 hours, -8 hours, etc.
3. **Identify geographical patterns** -cross-reference user location data (store locations, addresses) with expected timezone offsets
4. **Look for impossible timestamps** - dates that would be in the future when they were created
If most users are in predictable timezone patterns (like "mostly US customers" or "mostly West Africa"), we can reverse-engineer the original timezone and correct the data with reasonable confidence.
### Key Questions
- What's the distribution of time differences between createdAt and updatedAt?
- Is there clustering around common timezone offsets (+1, +5, -8 hours)?
- Are there records where createdAt is significantly after updatedAt (which would indicate timezone errors)?