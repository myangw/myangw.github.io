---
title: "Java Interface vs Abstract Class: When to Use What"
date: 2021-10-24T00:00:00+09:00
slug: "java-interface-versus-abstract-class-when-to-use-what"
tags:
  - Java
  - Interface
  - Abstract Class
draft: false
ShowToc: true
TocOpen: false
---

While "the distinction between interfaces and abstract classes" constitutes a common inquiry, investigation beyond superficial differences reveals remarkably diverse perspectives.

Java 8's introduction of default methods in interfaces substantially diminished the distinctions between the two constructs. This exposition examines in detail when each proves most appropriate.

## Fundamental Characteristics

Let us first examine the basic characteristics.

### Interface

- May contain constants (static final) and abstract methods

    ```java
    interface Barkable {
      public static final int BLABLA_CONSTANT = 1;
      public abstract void bark();
    }
    ```

- Java 8 introduced default methods (permitting complete implementation)
    - Default methods: Common code for implementing classes written in default methods reduces repetition

    ```java
    // Default method in java.util.List

    default void replaceAll(UnaryOperator<E> operator) {
            Objects.requireNonNull(operator);
            final ListIterator<E> li = this.listIterator();
            while (li.hasNext()) {
                li.set(operator.apply(li.next()));
            }
    }
    ```

    - Default method constraints:
        - Cannot reference implementation state
        - Object methods such as `equals` or `hashCode` should not be provided as default methods
- May possess static methods
    - Like default methods, implementation is possible in the interface
        - Distinction from default methods: Cannot be overridden
    - Being static methods, invocation follows `Class.method()` pattern
- A single implementation may implement multiple interfaces

### Abstract Class

- Declared with the `abstract` keyword

    ```java
    abstract class Animal {
    }
    ```

- May contain abstract methods
    - Abstract methods lack implementation
    - Abstract classes need not contain abstract methods, but classes containing abstract methods must be declared abstract
- Cannot be instantiated directly
    - Instantiation requires creating a class that extends the abstract class
- Abstract classes possess constructors and may maintain state

## Java 8 Interface Default Methods

### Rationale for Default Method Introduction

- Stack Overflow responses frequently reference "backward compatibility"
    - JDK developers faced code breakage when adding methods to interfaces due to cascading effects on implementing classes; hence, default methods were created to maintain compatibility
        - With implementation in the interface, adding new methods does not affect implementing classes
        - For example, the forEach method was added as a default method to the Collection interface, enabling lambda expression usage in existing interface parameters

            ```java
            public interface Iterable<T> {
                public default void forEach(Consumer<? super T> consumer) {
                    for (T t : this) {
                        consumer.accept(t);
                    }
                }
            }
            ```

        - (Default methods appear more pragmatically motivated by development necessities rather than initial design intent; hence the "backward" terminology)

## When to Use What

### When Abstract Classes Prove Preferable

- When clear hierarchical structure necessitates inheritance relationships, and common functionality implementation is required
- [Excellent exposition with code examples](https://javabypatel.blogspot.com/2017/07/real-time-example-of-abstract-class-and-interface-in-java.html) summarized briefly:
    - Implementing large-scale SMS sender - different carriers possess different towers requiring distinct implementations + common rules requiring enforcement (DoNotDisturb mode verification)
    - Abstracted SMS sending code:

    ```java
    public void sendSMS(){
       establishConnectionWithYourTower();
       checkIfDoNotDisturbMode();
       // -- Send SMS --
       destroyConnectionWithYourTower();
    }

    public void establishConnectionWithYourTower(){
    	// Varies by carrier
    }

    public void checkIfDoNotDisturbMode(){
    }

    public void destroyConnectionWithYourTower(){
    	// Varies by carrier
    }
    ```

    - Implementation:

    ```java
    abstract class SMSSender{

     abstract public void establishConnectionWithYourTower();

     public void sendSMS(){
       establishConnectionWithYourTower();
       checkIfDoNotDisturbMode();
       // -- Send SMS --
       destroyConnectionWithYourTower();
     }

     abstract public void destroyConnectionWithYourTower();

     public void checkIfDoNotDisturbMode(){
    	 // Implementation in abstract class
     }
    }

    /* Carrier classes extend SMSSender */
    class Vodafone extends SMSSender{
     @Override
     public void establishConnectionWithYourTower() {
    	// Vodafone-specific connection
     }

     @Override
     public void destroyConnectionWithYourTower() {
    	// Vodafone-specific termination
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

### When Interfaces Prove Preferable

'Effective Java' advocates "prefer interfaces to abstract classes" with multiple rationales and example cases.

1. Easier implementation of new interfaces in existing classes
    - Add interface-required methods and implement; complete.
    - Abstract classes permit only single inheritance; inserting new abstract classes forces subclasses to extend abstract classes in inappropriate contexts.
2. Appropriate for mixin definitions
    - Classes can declare provision of specific optional functionality "mixed in" beyond their primary type.
    - Example: Classes implementing `Comparable` declare instances can be ordered among Comparable implementations.
3. Enables hierarchyless type frameworks
    - Some concepts resist strict hierarchical classification
        - Example: Singer, Songwriter - classes may require implementing both. Without interfaces, each combination necessitates new abstract classes. Hierarchical accumulation leads to combinatorial explosion...

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

### Combining Interface and Abstract Class Advantages

⇒ Provide interfaces alongside abstract skeletal implementation classes

- Interfaces define types, providing default methods as necessary
- Skeletal implementation classes implement remaining methods
- ⇒ Follows the Template Method Pattern design pattern
- Example 1) Java Collection framework's AbstractList, AbstractMap, et cetera
    - Map interface exists with AbstractMap skeletal implementation
    - HashMap, TreeMap extend AbstractMap while SortedMap implements Map without extending AbstractMap
- Example 2) Object-oriented refactoring process in Cho Young-ho's 'Object' book. [Refer to well-organized exposition](https://justpanda.tistory.com/7) as excessive length prohibits inclusion
- Advantages: Provides implementation assistance like abstract classes + liberation from constraints imposed by abstract class type definition
- However, interface addition sometimes proves excessive in practice. Trade-offs necessitate context-appropriate decisions!

---

### References

- 'Effective Java' 3rd Edition - Joshua Bloch (Item 20. Prefer interfaces to abstract classes)
- 'Object' - Cho Young-ho (Chapter 2)
- [http://muhammadkhojaye.blogspot.com/2014/03/interface-default-methods-in-java-8.html](http://muhammadkhojaye.blogspot.com/2014/03/interface-default-methods-in-java-8.html)
- [https://javabypatel.blogspot.com/2017/07/real-time-example-of-abstract-class-and-interface-in-java.html](https://javabypatel.blogspot.com/2017/07/real-time-example-of-abstract-class-and-interface-in-java.html)
- [https://yaboong.github.io/java/2018/09/25/interface-vs-abstract-in-java8/](https://yaboong.github.io/java/2018/09/25/interface-vs-abstract-in-java8/)
- [https://velog.io/@chaean_7714/HeadFirst-java8-인터페이스-와-추상클래스](https://velog.io/@chaean_7714/HeadFirst-java8-%EC%9D%B8%ED%84%B0%ED%8E%98%EC%9D%B4%EC%8A%A4-%EC%99%80-%EC%B6%94%EC%83%81%ED%81%B4%EB%9E%98%EC%8A%A4)
