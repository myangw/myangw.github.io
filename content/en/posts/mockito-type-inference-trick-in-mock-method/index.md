---
title: "Understanding Mockito's Type Inference Trick in the mock() Method"
date: 2025-01-19T00:00:00+09:00
slug: "mockito-type-inference-trick-in-mock-method"
tags:
  - Java
  - Generic
draft: false
ShowToc: true
TocOpen: false
---

Recently, I nearly misinterpreted code authored by a team member contrary to its intended purpose. The implementation initially appeared counterintuitive, prompting thorough reinvestigation documented herein.

The team member's code utilized generics for creating a method applicable to API invocations in a versatile manner. The explanation referenced employing an identical technique to Mockito library's mock() method, warranting examination.

### Type Inference in Mockito's mock()
(Version: mockito-core 4.9 or higher, included in spring-boot-starter-test from 3.1 onwards)

How does the mock() method achieve type inference? Throughout test code authorship, I had utilized it unthinkingly without comprehending the underlying mechanism. Consider the following code:

```java
Money dollar = mock(Money.class);
Money euro = mock();
```

Both variables dollar and euro compile and execute without issues.

The dollar variable pattern, explicitly specifying the class for mocking, appears requisite. However, the euro variable pattern functions identically without explicit specification.

The internal method implementation appears as follows:

```java
@SafeVarargs
public static <T> T mock(T... reified) {
    return (T)mock(withSettings(), reified);
}
```

Deeper investigation of invoked methods reveals:

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

Superficially scanning the `mock()` method content:

- Appears to accept no arguments, yet actually possesses varargs for generic type variables.
- Must array creation for argument transmission be required? Negative. IllegalArgumentException occurs if reified is null or length exceeds 1.
    - The message states "Java will automatically detect the class, so provide no values." This unambiguously clarifies usage methodology.

❓ How does class detection occur?

This technique combines generic methods + array reified characteristics + varargs. Let us examine each component.

### 1. Generic Methods

Generic methods define type parameters at method level, enabling operation across diverse types.

```java
public static <T> T getFirstElement(T[] array) {
    return array[0];
}

String[] names = {"garlic", "onion"};
Integer[] scores = {1, 3};

String firstName = getFirstElement(names);
Integer firstScore = getFirstElement(scores);

Integer firstName = getFirstElement(names); // Compilation error!
```

String array arguments return String types; Integer array arguments return Integer types.

Return type T is determined by argument T[] type during method invocation, providing compile-time type safety.

### 2. Arrays are Reified

"Reified" signifies "concretized," though the Korean translation appears excessively generic, potentially causing confusion.

In programming, "reified" describes generic type information retention or utilization at runtime.

Unlike generics, array types persist at runtime. (Type erasure) Generic types remain valid exclusively at compile-time.

For example, `List<String>` type arguments become merely `List` at runtime. However, array types remain preserved at runtime.

### 3. Varargs (Variable Arguments)

Varargs enable methods to accept 0 to n arguments dynamically. Internally, new arrays are created.

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

Providing no varargs arguments results in length-0 array equivalent treatment. (Note: Explicitly passing null makes the parameter null)

Synthesizing comprehension while revisiting the mock() method:

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

1. Compile-time: euro's type declaration as `Money` enables compiler inference of generic type T as Money.
2. mock() invocation with no varargs arguments converts to length-0 array.
3. Array transmission preserves Money type information at runtime.
4. Length-0 array satisfies condition `if (reified != null && reified.length <= 0)` evaluating true
5. `getClassOf(reified)` invocation extracts type information from the array.

This technique proves beneficial when crafting generic methods for frequently utilized common functionality, enabling avoidance of explicit `Class<T>` parameter transmission. Witnessing such sophisticated language utilization inspires deeper language study aspiration.

### References

- Mockito PR merging this implementation:
https://github.com/mockito/mockito/pull/2779
