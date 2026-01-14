---
title: "Java interface vs abstract class - 언제 무엇을 쓸까"
date: 2021-10-24T00:00:00+09:00
slug: "Java interface vs abstract class - 언제 무엇을 쓸까"
tags:
  - Java
  - 인터페이스
  - 추상클래스
draft: false
ShowToc: true
TocOpen: false
---

'인터페이스와 추상클래스의 차이'는 흔한 질문같지만 표면적인 차이 이상으로 들어가다보니 꽤 다양한 생각들을 만날 수 있었다.

Java8에서 인터페이스에 '디폴트 메서드'를 추가할 수 있게 되어서 둘의 차이점이 많지 않아졌다. 언제 무엇을 쓰는게 바람직한가를 좀더 자세히 살펴봤다.

## 특징

먼저 기본적인 특징들을 살펴보자.

### 인터페이스

- 상수(static final ~) 와 추상메서드를 포함할 수 있다

    ```java
    interface Barkable {
      public static final int BLABLA_CONSTANT = 1;
      public abstract void bark();
    }
    ```

- Java8부터 디폴트 메서드 (안에 구현까지 작성 가능)를 포함할 수 있다
    - 디폴트 메서드: 인터페이스를 상속한 구현체에 공통으로 들어갈 코드를 디폴트 메서드에 작성하여 반복을 줄인다
    
    ```java
    // java.util.List에 있는 디폴트 메서드
    
    **default void replaceAll(UnaryOperator<E> operator) {
            Objects.requireNonNull(operator);
            final ListIterator<E> li = this.listIterator();
            while (li.hasNext()) {
                li.set(operator.apply(li.next()));
            }
    }**
    ```
    
    - default method 제약사항
        - 구현체의 state를 참조할 수 없다
        - `equals` 나 `hashCode` 같은 Object의 메서드 정의한건 디폴트 메서드로 제공해서는 안된다.
- 스태틱 메서드를 가질 수 있다
    - 디폴트 메서드처럼 인터페이스에서 구현이 가능하다
        - 디폴트 메서드와 차이점은, overriding할 수 없다는 것
    - 스태틱 메서드이므로 `클래스.메서드()` 로 호출
- 하나의 구현체가 여러개의 인터페이스를 구현(implement)할 수 있다

### 추상 클래스

- `abstract` 키워드와 함께 선언한다.
    
    ```java
    abstract class Animal {
    }
    ```
    
- 추상 메서드를 가질 수 있다.
    - 추상 메서드는 구현부가 없는 메서드이다.
    - 추상 클래스에 추상 메서드가 반드시 필요하진 않지만, 추상메서드를 포함하는 클래스는 추상 클래스로 선언되어야 한다.
- 그 자체로 인스턴스화 할 수 없다.
    - 인스턴스화하려면 추상 클래스를 상속한 클래스를 만들어야한다
- 추상클래스는 생성자가 있고, state를 들고있을 수 있다.

## Java8 interface의 default method

### 디폴트 메서드가 생긴 이유

- stackoverflow답변들을 보다보니 'backward compatibility'~~ 란 말이 있었다.
    - 무슨말인가 보니 JDK 개발자들이 코드를 수정할 때 인터페이스 하나에 메서드를 추가하면 줄줄이 그것을 구현하고 있는 클래스들 코드가 깨져서, 호환성을 유지하기 위해 디폴트 메서드를 만들었다고 한다.
        - 이미 있는 인터페이스에 새로운 메서드를 추가할 때 인터페이스 안에 구현이 있게되면 구현 클래스들에 영향을 받지 않기 때문.
        - 대표적인 예로 collection 인터페이스에 forEach 메서드가 디폴트 메서드로 추가되었는데, 이렇게 해서 기존에 있던 인터페이스의 파라미터에 lambda expression을 넣을 수 있게 되었다.
            
            ```java
            public interface Iterable<T> {
                public default void forEach(Consumer<? super T> consumer) {
                    for (T t : this) {
                        consumer.accept(t);
                    }
                }
            }
            ```
            
        - (디폴트 메서드를 처음부터 의도가 있어서 만들었다기보다 개발하다보니 필요해져서(?) 만든 것에 가까워서 'backward'라는 표현을 쓴 것 같다.)

## 언제 무엇을 쓸까

### 추상클래스를 쓰는 것이 좋은 경우

- 명확하게 계층구조가 필요하여 상속관계로 만들고, 공통된 기능 구현이 필요할 때
- [코드 예시를 든 좋은 글](https://javabypatel.blogspot.com/2017/07/real-time-example-of-abstract-class-and-interface-in-java.html)이 있어서 간단히 요약:
    - 대용량 SMS sender를 구현 - 여러 나라의 통신사들이 다른 tower를 갖고 있어서 각각 다른 구현이 필요 + 공통으로 지켜야할 규칙(DoNotDisturb모드인지 확인) 도 있는 상황일 때
    - SMS를 보내는 추상화된 코드:
    
    ```java
    public void sendSMS(){
       establishConnectionWithYourTower();
       checkIfDoNotDisturbMode();
       // -- SMS 보내기 --
       destroyConnectionWithYourTower();
    }
    
    public void establishConnectionWithYourTower(){
    	// 통신사마다 다르다
    }
    
    public void checkIfDoNotDisturbMode(){
    }
     
    public void destroyConnectionWithYourTower(){
    	// 통신사마다 다르다
    }
    ```
    
    - 구현
    
    ```java
    abstract class SMSSender{
      
     abstract public void establishConnectionWithYourTower();
      
     public void sendSMS(){
       establishConnectionWithYourTower();
       checkIfDoNotDisturbMode();
       // -- SMS 보내기 --
       destroyConnectionWithYourTower();
     }
     
     abstract public void destroyConnectionWithYourTower();
     
     public void checkIfDoNotDisturbMode(){
    	 // 추상클래스 안에서 구현
     }
    }
    
    /* SMSSender를 통신사 클래스들이 상속 */ 
    class Vodafone extends SMSSender{
     @Override
     public void establishConnectionWithYourTower() {
    	// Vodafone 방식으로 커넥션 맺기
     }
     
     @Override
     public void destroyConnectionWithYourTower() {
    	// Vodafone 방식으로 커넥션 종료
     } 
    }
     
    class Airtel extends SMSSender{
     @Override
     public void establishConnectionWithYourTower() {
     }
     
     @Override
     public void destroyConnectionWithYourTower() {
     }
    }
    ```
    

### 인터페이스를 쓰는 것이 좋은 경우

책 '이펙티브 자바'에서는 '추상클래스보다 인터페이스를 우선하라'고 하며 여러 이유와 예시 케이스들을 든다.

1. 기존 클래스에 새로운 인터페이스 구현이 쉽다
    - 인터페이스가 요구하는 메서드들을 추가하고, implements하면 끝.
    - 추상클래스로는 단일 상속만 가능하므로, 새로 추상클래스를 끼워 넣으면 적절하지 않은 상황에서 서브클래스들이 추상클래스를 상속받는다.
2. mixin 정의 시 적절하다
    - 클래스의 원래의 주된 타입 외에 특정한 다른 선택적 기능을 'mix in'하여 제공한다고 선언하는 효과를 줄 수 있다.
    - ex. 어떤 클래스가 `Comparable` 을 구현하면, `Comparable` 을 구현한 인스턴스들끼리는 순서를 정할 수 있다고 선언하는 것.
3. 계층구조가 없는 타입 프레임워크를 만들 수 있다
    - 계층을 엄격하게 구분하기 어려운 개념들도 있다
        - ex. Singer, Songwriter - 둘 다를 구현하는 클래스가 필요할 수 있다. 이걸 인터페이스를 쓰지 않는다면 조합마다 매번 새로운 abstract클래스를 사용하게 됨. 이런 계층이 쌓이고 쌓이면 조합 폭발...
            
            ```java
            // interface
            public interface SingerSongWriter extends Singer, SongWriter {
            	void actSensitive();
            }
            
            // abstract class
            public abstract class SingerSongWriter {
            	abstract AudioClip sing(Song s);
            	abstract Song compose(int chartPosition);
            	void actSensitive();
            }
            ```
            

### 인터페이스와 추상클래스의 장점을 모두 취하는 방법

⇒ 인터페이스와 추상 골격 구현 (skeletal implementation) 클래스를 함께 제공하기

- 인터페이스로는 타입을 정의하고, 필요 시 디폴트 메서드 제공
- 골격 구현 클래스는 나머지 메서드들 구현
- ⇒ 디자인패턴 중 '템플릿 메서드 패턴'을 따르는 방법이다.
- ex 1) Java Collection framework의 AbstractList, AbstractMap, etc.
    - interface로 Map이 있고 골격구현 클래스로 AbstractMap이 있다.
    - HashMap, TreeMap 등은 AbstractMap을 상속하지만 SortedMap은 AbstractMap을 상속하지 않고 Map을 구현한다.
- ex 2) 조영호 - '오브젝트' 책에도 추상클래스를 이 방식으로 리팩토링하는 과정이 나온다. 글이 너무 길어질 듯 하여  [잘 정리된 링크 참조](https://justpanda.tistory.com/7) :-)
- 이 방법의 장점 : 추상클래스처럼 구현을 도와주면서 + 추상클래스로 타입을 정의할 때 생기는 제약에서 자유롭다.
- 다만 현실적으로 인터페이스를 추가하는 것이 과할 때가 있다. 트레이드오프이므로 상황에 맞게!

---

### References

- 'Effective Java' 3판 - 조슈아 블로크 (item20. 추상클래스보다는 인터페이스를 우선하라)
- '오브젝트' - 조영호 (Chapter 2)
- [http://muhammadkhojaye.blogspot.com/2014/03/interface-default-methods-in-java-8.html](http://muhammadkhojaye.blogspot.com/2014/03/interface-default-methods-in-java-8.html)
- [https://javabypatel.blogspot.com/2017/07/real-time-example-of-abstract-class-and-interface-in-java.html](https://javabypatel.blogspot.com/2017/07/real-time-example-of-abstract-class-and-interface-in-java.html)
- [https://yaboong.github.io/java/2018/09/25/interface-vs-abstract-in-java8/](https://yaboong.github.io/java/2018/09/25/interface-vs-abstract-in-java8/)
- [https://velog.io/@chaean_7714/HeadFirst-java8-인터페이스-와-추상클래스](https://velog.io/@chaean_7714/HeadFirst-java8-%EC%9D%B8%ED%84%B0%ED%8E%98%EC%9D%B4%EC%8A%A4-%EC%99%80-%EC%B6%94%EC%83%81%ED%81%B4%EB%9E%98%EC%8A%A4)