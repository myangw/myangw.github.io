---
title: "Generic Type Variance: Invariance, Covariance, and Contravariance"
date: 2021-11-07T00:00:00+09:00
slug: "generic-variance-invariance-covariance-contravariance"
tags:
  - Java
  - Generic
  - Covariance
  - Contravariance
  - Type Variance
draft: false
ShowToc: true
TocOpen: false
---

While working with Spring Batch, I encountered ItemWriter's method `void write(List<? extends T> var1)` and pondered the rationale for such generic type specification. I have finally undertaken comprehensive investigation.

Contravariance concepts proved conceptually challenging, requiring several hours to achieve comprehension. However, upon understanding, the underlying principles appear remarkably straightforward. This exposition attempts maximal clarity.

## Generic Terminology

Initially, I had forgotten even the appropriate search terminology, necessitating terminological review. These terms follow Effective Java conventions.

- `?` : wildcard. Represents unknown type
- `List<?>`: unbounded wildcard type
- `List<? extends Integer>`, `List<? super Integer>` : bounded wildcard types
    - `? super Integer` : Integer or Integer's supertype
    - `? extends Integer` : Integer or Integer's subtype
- `E` : formal type parameter
- `List<E>` : generic type

## Invariance, Covariance, Contravariance

- Relationships between types and subtypes
- Translatable as invariance, covariance, and contravariance respectively... English terminology proves more comprehensible
    - in- denotes negation, co- signifies together, contra- indicates opposition
    - covariant: If A is B's subtype, then f(A) is f(B)'s subtype
    - contravariant: If A is B's subtype, then f(B) is f(A)'s subtype
    - invariant: Neither of the above applies

### Invariance

```java
interface Animal {
	void eat()
}
class Panda extends Animal {
	void eat()
}
```

- While Panda constitutes Animal's subtype, `List<Panda>` does not constitute `List<Animal>`'s subtype.
    - Panda can perform Animal's operations (eat()) without issue,
    - However, `List<Panda>` cannot perform `List<Animal>`'s operations (adding various Animal types) since it accepts only Panda types
- ⇒ The non-preservation of class inheritance relationships in Generics is termed Invariance
Generics undergo type erasure during compilation. At runtime, the JVM recognizes only List objects in this example.

- Scenarios such as the following code cannot compile under Invariance:

```java
void copyAll(Collection<Object> to, Collection<String> from) {
    to.addAll(from);
}
```

⇒ Bounded wildcard types maximize flexibility in such circumstances.

### Covariance

- `? extends T`(Kotlin: `<out T>`)
- Since String is Object's subtype, `Collection<String>` may be utilized as `Collection<? extends Object>`'s subtype

- List<? extends T> permits read(get) operations exclusively; add operations are prohibited. (Rationale provided below)

```java
List<Double> doubles = Arrays.asList(1.1, 2.2, 3.3);
List<? extends Number> numbers = doubles; // permissible

Number number = numbers.get(0);
System.out.println(number);
numbers.add(1.1); // compilation error
```

### Contravariance

- `? super T` (Kotlin: `<in T>`)
- Integer is Number's subtype → `Collection<Number>` may be utilized as `Collection<? super Integer>`'s subtype

- `List<? super T>` prohibits read(get) operations; add operations are permitted. (Rationale provided below)

```java
public void addNumber(List<? super Integer> numbers) {
    numbers.add(6);
    // numbers.get(0); compilation error
}

List<Number> myInts = new ArrayList<>();
addNumber(myInts);

System.out.println(myInts); // successful
```

## PECS Principle

When should `<? extends T>` versus `<? super T>` be employed?

Effective Java introduces the PECS mnemonic for guidance.

- **producer-extends, consumer-super.** (Alternative nomenclature: Get and Put Principle)
- When parameterized type T serves as producer, employ `<? extends T>`; when serving as consumer, employ `<? super T>`.
    - producer : Provides data. Read-only
    - consumer: Receives and utilizes information. Write-only
    - Initial confusion: if consumer receives information, shouldn't consumer perform read operations?
        - For instance, considering `List<T>` from 'List's perspective'
        - → A producer provides read capability, while consumer receives external write operations
- Important: Avoid bounded wildcards in method return types. Client code would necessitate wildcard type usage, diminishing flexibility.

    ```java
    public T method1() {} // appropriate
    public <? extends T> method2() {} // inappropriate!
    ```

## Rationale for Exclusive add/get Capabilities

- While the PECS principle is comprehensible, understanding its foundational logic proved intriguing.

- Essential considerations:
    - Child objects encompass all parent object methods plus additional capabilities. Consequently, child objects can substitute parent objects, but parent objects cannot substitute child objects.
    - Assigning parent to child produces compilation errors, as parents lack complete child capabilities.

- Revisiting the covariance example:

```java
List<Double> doubles = Arrays.asList(1.1, 2.2, 3.3);
List<? extends Number> numbers = doubles; // permissible

Number number = numbers.get(0);
	// Any object retrieved from numbers is Number type or
	// upcasts to Number type, enabling compilation

numbers.add(1.1); // compilation error
                    // Though Double is Number's subtype, potentially perplexing,
                    // the List might contain types more specific than Double,
                    // preventing Double addition with type safety guarantees.
```

- Examining the contravariance example:

```java
public void addNumber(List<? super Integer> numbers) {
    numbers.add(6); // List stores Integer and Integer supertypes,
										// permitting Integer type addition.

		int a = numbers.get(0); // compilation error
                                // Parent classes coexist in storage,
                                // providing no guarantee of Integer retrieval possibility.
}
```

Covariance and contravariance represent unified concepts rather than disparate phenomena.

When extracting T from `Collection<T>`, `Collection<T>` serves as producer. `Collection<? extends T>` enables flexibility while enforcing read-only constraints.

When inserting T into `Collection<T>`, `Collection<T>` serves as consumer, with `Collection<? super T>` enabling write-only constraints.

---

### References

- 'Effective Java' 3rd Edition Item 31 ⭐
- [https://stackoverflow.com/questions/2723397/what-is-pecs-producer-extends-consumer-super/19739576#19739576](https://stackoverflow.com/questions/2723397/what-is-pecs-producer-extends-consumer-super/19739576#19739576) → PECS comprehension assistance
- [https://s2choco.tistory.com/21](https://s2choco.tistory.com/21) → PECS comprehension assistance
- [https://codechacha.com/ko/java-covariance-and-contravariance/](https://codechacha.com/ko/java-covariance-and-contravariance/) → Examples
