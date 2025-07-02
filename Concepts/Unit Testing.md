- Don't use constructors in unit tests, instead use the Setup or Initialise method provided the framework. Each test should work with a fresh instance of whatever dependencies are used. You do **NOT** want your unit tests to share state.
- Mocking `SignInManager` and `UserManager`:

```
	_userManagerMock = new Mock<UserManager<ApplicationUser>>(  
    Mock.Of<IUserStore<ApplicationUser>>(),  
    null!, null!, null!, null!, null!, null!, null!, null!);
      
_signInManagerMock = new Mock<SignInManager<ApplicationUser>>(  
    _userManagerMock.Object,  
    Mock.Of<IHttpContextAccessor>(),  
    Mock.Of<IUserClaimsPrincipalFactory<ApplicationUser>>(), null!, null!, null!, null!);
```

- Testing your JWT generation function is good practice. It helps ensure that:
	1. The function correctly generates a token.
	2. The token contains the expected claims.
	3. The token is signed using the correct security key and algorithm.
	4. The token's expiration time is set correctly.
	5. The token issuer and audience are configured as expected.

