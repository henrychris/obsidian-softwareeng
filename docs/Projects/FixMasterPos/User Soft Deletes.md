When an order is created, the user who created it is linked to the order using the `createdBy` field. Similarly, the user is mentioned in the timeline using the same field.
Now, we want to soft-delete users instead.

## Steps
1. Add `deletedBy` and `deletedAt` fields to the user model.
2. Update `checkLogin` in `auth.middleware.ts` to find users where `deletedAt` is not null.
	- If we update this, then it cascades to the endpoints that call it. So, should i also update those endpoints to exclude deleted users? 
3. Update `getUsers`, `getUserDetails`, `updateUser`, `pinVerification`, `rolesAndStaff`, `exportUsers`, `exportUsersWithID`, `attachCouponToUser` in `user.controller` to excluded deleted users.