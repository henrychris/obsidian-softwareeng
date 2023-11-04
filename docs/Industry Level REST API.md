# ErrorOr
My main takeaway from [this](https://www.youtube.com/watch?v=PmDJIooZjBE) video is the ErrorOr library. In a nutshell, it allows one to return either an error from a function, or the result of the successful operation. It makes error handling a bit easier too, as in some cases you can add all errors that occurred, instead of just the first.

Take this function and NotFound property:
```
public static Error NotFound => Error.NotFound(  
    code: "Event.NotFound",  
    description: "Event not found.");

public async Task<ErrorOr<EventResponse>> GetEvent(string id)  
{  
    var result = await _dbContext.Events.FindAsync(id);  
    return result is not null ? _mapper.Map<EventResponse>(result) : Errors.Event.NotFound;  
}
```

`Errors.Event.NotFound` is a type of error within the library that I used for situations where the event wasn't found. As you can see, we can either return the result or the error - anyone works.

Next, the controller where the GetEvent() method is called:

```
/// <summary>  
/// Retrieves an event by its unique identifier.  
/// </summary>  
/// <param name="id">The unique identifier of the event to retrieve.</param>  
/// <returns>  
/// - If the event is found, it returns an HTTP 200 (OK) response with an ApiResponse containing the event data.  
/// - If the event is not found or an error occurs, it returns an appropriate error response. 
/// </returns>  
[HttpGet("{id:guid}")]  
public async Task<IActionResult> GetEvent(Guid id)  
{  
    var getEventResult = await _eventService.GetEvent(id.ToString());  
  
	 // If successful, return the event data in an ApiResponse.  
	 // If an error occurs, return an error response using the ReturnErrorResponse method     	 return getEventResult.Match(  
        _ => Ok(getEventResult.ToSuccessfulApiResponse()),  
        ReturnErrorResponse);  
}
```

The Match method can handle a variety of outcomes. In this scenario, the first entry handles all scenarios that are not errors, while ReturnErrorResponse handles the error that is returned to the client.
The `ToSuccessfulApiResponse` method takes the value returned from GetEvent and creates an ApiResponse object which is sent to the user.
```
public static ApiResponse<T> ToSuccessfulApiResponse<T>(this ErrorOr<T> errorOr)  
{  
    return new ApiResponse<T>(data: errorOr.Value, message: "Success", success: true);  
}
```

For more info, refer to the project.
Related: [[Event Management API]]


# Best Practices
1.  As a general guideline for REST APIs, path parameters should be used for resource identification while query parameters should be used for resource sorting and filtering.