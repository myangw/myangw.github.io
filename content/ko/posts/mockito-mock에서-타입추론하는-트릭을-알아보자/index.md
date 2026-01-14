---
title: "Mockito mock()에서 타입추론하는 트릭을 알아보자"
date: 2025-01-19T00:00:00+09:00
slug: "Mockito mock()에서 타입추론하는 트릭을 알아보자"
tags:
  - java
  - generic
draft: false
ShowToc: true
TocOpen: false
---

최근 팀원이 짜놓은 코드를 의도와 다르게 해석할뻔한 경험이 있었다.  ‘이게 왜 되지’하며 바로 이해되지 않았었는데, 차근차근 다시 찾아보며 글을 남겨본다.

팀원의 코드는 api 호출을 할 때 범용적으로 사용할 수 있도록 제네릭을 사용한 메서드였다. Mockito 라이브러리의 mock() 메서드와 동일한 트릭을 썼다고 설명을 해주셔서 살펴봤다. 

### Mockito의 mock() 에서 타입 추론
(version: mockito-core 4.9 이상, spring-boot-starter-test에선 3.1부터 포함됨)

mock() 메서드는 어떻게 타입 추론을 하는걸까? 지금껏 테스트코드를 짤 때 무심코 잘 쓰기만 하고 왜 되는지는 몰랐다. 아래 코드를 보자.

```java
Money dollar = mock(Money.class);
Money euro = mock();
```

변수 dollar, euro 모두 컴파일과 런타임 시 실행에 아무런 문제가 없다. 

변수 dollar처럼 어떤 클래스를 mocking하는지 알려줘야할 것 같지만, 변수 euro 와 같이 쓰는데도 문제가 없는 것.

내부 메서드 구현은 아래 코드처럼 되어있다.

```java
@SafeVarargs
public static <T> T mock(T... reified) {
    return (T)mock(withSettings(), reified);
}
```

안에서 호출하는 메서드들을 더 들어가보면:

```java
@SafeVarargs
public static <T> T mock(MockSettings settings, T... reified) {
    if (reified != null && reified.length <= 0) {
        return (T)mock(getClassOf(reified), settings);
    } else {
        throw new IllegalArgumentException("Please don't pass any values here. Java will detect class automagically.");
    }
}

private static <T> Class<T> getClassOf(T[] array) {
    return array.getClass().getComponentType();
}
```

표면적으로 `mock()`메서드 내용을 스캔해보자.

- 메서드 인자로 아무것도 넘겨주지 않는 것 같았지만 사실 제네릭 타입변수에 대한 가변인자가 있다.
- 무언가를 배열로 만들어서 인자로 넘겨줘야하나? 아니다. reified가 null이거나 length가 1이상이면 IllegalArgumentException을 터뜨린다.
    - 메시지는 “Java가 알아서 class를 디텍팅할테니 아무 값도 넘기지마세요” 라고 되어있다. 이로써 사용법 자체는 누가 봐도 확실하게 알 수 있는 것 같다.

❓그런데 어떻게 class를 알아내는걸까? 

이 트릭은 제너릭 메서드 + 배열의 reified 특성 + 가변인자 를 함께 이용했다. 하나씩 살펴보자.


### 1. 제네릭 메서드

제네릭 메서드는 메서드 레벨에서 타입 파라미터를 정의해서 다양한 타입에 대해 동작한다. 

```java
public static <T> T getFirstElement(T[] array) {
    return array[0];
}

String[] names = {"garlic", "onion"};
Integer[] scores = {1, 3};

String firstName = getFirstElement(names);
Integer firstScore = getFirstElement(scores);

Integer firstName = getFirstElement(names); //컴파일 에러!
```

String배열을 인자로 넣었을 때 String 타입을 리턴하고, Integer배열을 넣으면 Integer 타입을 리턴한다.

리턴타입 T는 메서드를 호출 할 때 argument T[]에 어떤 타입을 전달하느냐에 따라 결정되며, compile 타임에 타입 안전성을 제공한다.

### 2. 배열은 reified

reified는 ‘구체화된’ 이라는 뜻인데 한국어 단어로 그냥 쓰면 너무 보편적인? 느낌이라 혼동의 여지가 있는 것 같다. 

프로그래밍에선 제네릭과 관련된 내용을 설명할 때 사용된다. “reified”라는 말은 런타임에 제네릭 타입 정보를 유지하거나 활용할 수 있다는 것을 말한다.

runtime시 배열과 달리 제네릭의 타입은 소거된다. (type erase) 제네릭의 타입은 컴파일 시점에만 유효한 것.

예를들어 `List<String>`타입을 인자로 넣을 때, runtime 시점에는 그냥 `List` 가되어버린다. 그렇지만 배열의 타입은 런타임 시 유지가 된다.

### 3. 가변인자 (varargs)

가변인자를 사용하면 메서드의 인자를 0개부터 n개까지 동적으로 넣을 수 있다. 내부적으로는 배열을 새로 생성한다. 

```java
static String concat(String ... names) {
    StringBuilder sb = new StringBuilder();
    for (String name : names) {
        sb.append(name).append(",");
    }
    return sb.toString();
}

String[] names1 = {"garlic"};
String[] names2 = {"garlic", "onion"};

String x = concat(); // ""
String y = concat(names1); // "garlic,"
String z = concat(names2); // "garlic,onion,"
```

가변인자에 아무것도 넣지 않으면 length가 0인 배열과 동일하게 처리한다. (참고로 명시적으로 null을 전달하면 파라미터는 null이 된다)


다시 mock()메서드를 보면서 종합해보자.

```java
Money euro = mock();

@SafeVarargs
public static <T> T mock(MockSettings settings, T... reified) {
    if (reified != null && reified.length <= 0) {
        return (T)mock(getClassOf(reified), settings);
    } else {
        throw new IllegalArgumentException("Please don't pass any values here. Java will detect class automagically.");
    }
}

private static <T> Class<T> getClassOf(T[] array) {
    return array.getClass().getComponentType();
}
```

1. 컴파일 시점에 euro의 타입이 `Money` 로 선언되어 있기 때문에 컴파일러는 제네릭 타입 T를 Money로 추론한다.
2. mock()은 호출시점에 가변인자에 아무것도 넣지 않기 때문에 길이가 0인 배열로 변환된다.
3. 배열로 전달하기 때문에 런타임 시에도 Money라는 타입 정보를 유지할 수 있다.
4. 배열의 길이가 0이므로 조건문 `if (reified != null && reified.length <= 0)`  에서 true
5. `getClassOf(reified)` 를 호출하면서 배열에서 타입정보를 얻을 수 있다.


#


제네릭을 활용해서 공통으로 자주 사용하는 메서드를 짤 때, `Class<T>`를 일일이 넘기지 않게 하고 싶을 때 활용해보면 유익할 것 같다. 언어를 정말 잘 아는 사람은 이렇게까지 활용하는구나 싶어서 언어를 더 깊게 공부해보고싶어졌다. 

### 참고

- mockito에 위 내용이 merge 된 PR:
https://github.com/mockito/mockito/pull/2779 
