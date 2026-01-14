---
title: "Spring Security: Login Failure Handling After N Attempts - A Journey of Troubleshooting"
date: 2021-12-19T00:00:00+09:00
slug: "spring-security-login-failure-handling-journey"
tags:
  - Spring Security
draft: false
ShowToc: true
TocOpen: false
---

Recently, I have undertaken Spring Security authentication logic implementation in production environments for the first time. Fundamental functionalities such as login, registration, and authorization proved relatively straightforward owing to abundant tutorials and documentation. However, implementing seemingly trivial auxiliary requirements presented greater challenges. Among these, the troubleshooting process culminating in error handling for multiple consecutive incorrect password entries merits documentation.

- Initially, I attempted to utilize the `AuthenticationFailureHandler` interface implementation created for REST API development.
    - (The default FailureHandler proves unsuitable due to login page redirection logic. Spring Security's default form authentication necessitates failure handler implementation that returns 401 HTTP status without redirection for REST API compatibility.)
    - This FailureHandler would perform counting upon each login failure, displaying error messages upon exceeding n attempts. As the class responsible for post-authentication failure, it appeared more appropriate than ProviderManager.

- Consequently, I commenced logic implementation resembling the following code:

```kotlin
@Component
class CustomLoginFailureHandler(
	val userService: UserService
) : AuthenticationFailureHandler {

    override fun onAuthenticationFailure(
        request: HttpServletRequest?,
        response: HttpServletResponse?,
        exception: AuthenticationException?
    ) {
		val readString = request.reader.lines().collect(Collectors.joining())
		val jsonRequest: Map<String, String> = objectMapper.readValue(readString)
		val username = jsonRequest.getOrDefault(USERNAME_PARAM, "")
		val count = userService.incrementFailCount(username)
		// ....
}
```

(Assuming count storage in database columns. Code reads request to extract username for service layer transmission for count increment)

- The issue: Request reading proved impossible
    - POST-transmitted "application/json" body reading via `request.reader.lines().collect(Collectors.joining())` produced empty results. Alternative methodologies yielded identical outcomes...
    - Pre-FailureHandler request reading verification via debugging confirmed successful reading
    - The issue originated from `AbstractAuthenticationProcessingFilter` interface implementations containing request reading logic for authentication, with read requests proving unrereadable subsequently
        - → Why???
        - HttpServletRequest's InputStream prohibits repeated reading

### Contemplated Solutions

1. Servlet Filter layer request InputStream reading with HttpServletRequestWrapper implementation enabling re-reading
    - → Layer boundary violation, with difficulty comprehending impacts on other project code. Not implemented
2. Share username between initial request reading implementation and FailureHandler? Read username from SecurityContextHolder in FailureHandler
    - → Nonexistent.. SecurityContextHolder stores authenticated users, not unauthenticated usernames
3. ProviderManager assumes partial failure logic responsibility ✅

    Override ProviderManager, incrementing login failure count upon authentication failure (password mismatch). Upon exceeding failure count, throw AuthenticationException with exception message → FailureHandler writes exception appropriately for transmission.

    More specifically, create AuthenticationProvider class extending `AbstractUserDetailsAuthenticationProvider`, with internal implementation closely following default `DaoAuthenticationProvider`, inserting desired logic into authentication failure sections.

    ```kotlin
    @Throws(AuthenticationException::class)
    override fun additionalAuthenticationChecks(
        userDetails: UserDetails,
        authentication: UsernamePasswordAuthenticationToken
    ) {
        if (authentication.credentials == null) {
            logger.debug("Failed to authenticate since no credentials provided")
            throw BadCredentialsException(
                messages.getMessage("AbstractUserDetailsAuthenticationProvider.badCredentials", "Bad credentials")
            )
        }
        val presentedPassword = authentication.credentials.toString()
        if (!this.passwordEncoder.matches(presentedPassword, userDetails.password)) {
            logger.debug("Failed to authenticate since password does not match stored value")
            handleAuthenticationFail(userDetails.username) // Newly added
            throw BadCredentialsException(
                messages.getMessage("AbstractUserDetailsAuthenticationProvider.badCredentials", "Bad credentials")
            )
        }
    }

    private fun handleAuthenticationFail(username: String) {
     // Implementation
     // Increment count; throw BadCredentialsException if failures exceed time threshold
    }
    ```

    Response processing in FailureHandler.

    For example:

    ```kotlin
    httpStatus: 401

    {
    	"message": "Login failed 5 or more times"
    }
    ```

    FailureHandler implementation for this response:

    ```kotlin
    response?.contentType = MediaType.APPLICATION_JSON_VALUE
    response?.status = HttpStatus.UNAUTHORIZED.value()

    response?.writer?.append(
        objectMapper().writeValueAsString(
            FailureResponse(exception?.message)
        )
    )

    data class FailureResponse(val message: String?)
    ```

This exposition may receive updates. While operational verification succeeded, lingering uncertainty regarding superior methodologies persists.

Full code will be shared if comprehensive tutorials are authored subsequently.

** Superior methodologies: please comment 🙏

### References

[https://meetup.toast.com/posts/44](https://meetup.toast.com/posts/44)

[https://gregor77.github.io/2021/05/18/spring-security-03/](https://gregor77.github.io/2021/05/18/spring-security-03/)
