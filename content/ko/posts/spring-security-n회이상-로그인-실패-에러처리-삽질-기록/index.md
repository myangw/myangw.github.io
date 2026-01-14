---
title: "Spring security - N회이상 로그인 실패 에러처리 삽질 기록"
date: 2021-12-19T00:00:00+09:00
slug: "Spring security - N회이상 로그인 실패 에러처리 삽질 기록"
tags:
  - Spring security
draft: false
ShowToc: true
TocOpen: false
---

요즘 처음으로 실무에서 Spring security로 인증 관련 로직을 구현하고 있다. 기본 로그인, 회원가입, 권한설정 등은 튜토리얼이나 문서가 많아 다소 쉽게 해결했는데, 별거 아닌듯한 부가적인 요구사항을 덧붙이는게 오히려 더 적용이 어려웠다. 그 중  로그인을 하다가 비밀번호를 여러번 잘못 치면 ‘n회연속 입력 오류’ 같은 에러 처리를 하기까지의 삽질 과정과 나름의 해결방법을 정리해봤다. 

- 먼저 Rest API로 개발하기 위해서 만들어둔 *`AuthenticationFailureHandler`* 인터페이스의 구현체를 이용하려고 했다.
    - (디폴트 FailureHandler를 쓰지 않는 이유는 로그인 페이지로 redirect하는 로직이 있기 때문이다. spring security에서 로그인 페이지에서 form인증을 하는게 디폴트라, Rest api 구현을 위해서는 로그인 실패 시 handler에서 redirect 없이 + 401 http status를 리턴해야한다.)
    - 이 FailureHandler에서 로그인 실패시마다 카운팅을 하고, 숫자가 n회를 초과하면 에러메시지를 띄우면 되겠다고 생각했다. 인증 후의 실패를 담당하는 클래스이니 ProviderManager보다 더 책임을 수행하기에 적합하다고 생각했다.

- 그래서 다음 코드와 같은 로직을 짜기 시작했다.

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

(우선 count는 db컬럼에 저장한다고 가정한다. count를 증가시킬 유저를 알기 위해서 request를 읽어서 username을 받아 service레이어로 넘기는 코드)

- 문제는 여기서 request를 읽을 수 없다는 것이었다.
    - POST로 전달된 “application/json”타입 body를 읽기 위한`request.reader.lines().collect(Collectors.joining())` 수행 결과가 빈 값이 나왔다. 이렇게 읽는게 아닌가? 하고 다른 방법을 찾아봤지만 똑같았다...
    - 그렇다면 FailureHandler로 오기 전에도 request를 읽을 수 없는지를 확인해봤다. 디버깅을 찍어보니 잘만 읽었다.
    - 문제 원인은 `AbstractAuthenticationProcessingFilter` 인터페이스의 구현체에서 인증을 위해 request를 읽는 로직이 있었고, 한번 읽은 로직을 다시 읽을 수 없기 때문이었다.
        - → 왜???
        - HttpServletRequest의 InputStream은 한번 읽으면 다시 읽을 수 없도록 막혀있다. ㅠ

### 생각해본 해결방법들

1. ServletFilter 레이어에서 request의 InputStream을 읽고 다시 읽을 수 있게 InputStream을 생성해서 돌려주는 HttpServletRequestWrapper를 구현하자
    - → Servlet을 건드리는건 layer를 침범하며, 이렇게 했을 때 프로젝트의 다른 코드에 미치는 영향들을 다 파악하기 어렵다. 구현 안해보고 패스
2. request를 최초로 읽는 구현체와 FailureHandler가 request의 username을 공유하기만 하면 되지 않을까? FailureHandler에서 SecurityContextHolder에 있는 username을 읽어오자
    - → 없다 ^^.. SecurityContextHolder는 인증된 사용자를 저장하지, 인증안된 username을 저장하지 않는다
3. 인증을 수행하는 ProviderManager에서 실패로직 처리 일부를 맡기자 ✅
    
    ProviderManager를 오버라이딩 하고, 여기서 인증 실패 시 (비밀번호 match되지 않을 때) 로그인실패 횟수를 증가시킨다. 실패횟수가 초과하면 AuthenticationException을 throw하는 부분에서 exception메시지와 함께 throw → FailureHandler에서 exception을 적절한 형태로 write해서 내보낸다.
    
    좀더 자세히 설명하면
    
    정확히는 `AbstractUserDetailsAuthenticationProvider` 를 상속한 AuthenticationProvider 클래스를 만들었고, 내부 구현은 디폴트로 적용되는 *`DaoAuthenticationProvider`* 를 거의 그대로 따르고 인증 실패 부분에 원하는 로직만 끼워 넣었다.
    
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
            handleAuthenticationFail(userDetails.username) // 새로 추가 
            throw BadCredentialsException(
                messages.getMessage("AbstractUserDetailsAuthenticationProvider.badCredentials", "Bad credentials")
            )
        }
    }
    
    private fun handleAuthenticationFail(username: String) {
     // 구현
     // 여기서 count를 증가시키고, count가 시간 내에 실패하면 BadCredentialsException을 던졌다
    }
    ```
    
    그리고 response는 FailureHandler에서 처리.
    
    예를 들어 
    
    ```kotlin
    httpStatus: 401
    
    {
    	"message": "5회 이상 로그인 실패"
    }
    ```
    
    를 리턴하고 싶다면 아래와같이 FailureHandler를 구현한다.
    
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
    

이 글은 업데이트 될 수 있다. 잘 동작하는 걸 확인했지만, 더 쉬운 방법이 있을텐데 하는 아쉬움이 남아있다.

full code는 나중에 좀더 상세한 튜토리얼을 쓴다면 공유 :) 

** 더 좋은 방법을 아신다면 댓글을 남겨주세요🙏

### References

[https://meetup.toast.com/posts/44](https://meetup.toast.com/posts/44) 

[https://gregor77.github.io/2021/05/18/spring-security-03/](https://gregor77.github.io/2021/05/18/spring-security-03/)