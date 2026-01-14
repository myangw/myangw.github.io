---
title: "Utilizing JPA @ElementCollection with Kotlin: Technical Implementation Guide"
date: 2023-02-26T00:00:00+09:00
slug: "utilizing-jpa-elementcollection-with-kotlin"
tags:
  - JPA
draft: false
ShowToc: true
TocOpen: false
---

Recently, I had the opportunity to utilize JPA's `@ElementCollection` feature in production code after an extended period. Due to substantial knowledge decay and absence of documented reference materials, the initial implementation required extensive research and deliberation, during which various errors were encountered. This article presents a concise compilation of key considerations.

### Understanding `@ElementCollection`

- JPA's `@ElementCollection` annotation is employed for mapping value type collections.
- It is utilized when referencing collections defined not as @Entity but as basic types or Embeddable classes.
- At the database level, this creates a separate table.

Consider a simplified example where a User's "Application" entity exists, and multiple "desired dates" can be selected:

```kotlin
@Entity
class Apply(
    userId: Long,
    desiredDates: MutableList<LocalDate>
) {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0

    val userId: Long = userId

    @ElementCollection
    @CollectionTable(name = "apply_desired_date", joinColumns = [JoinColumn(name = "apply_id")])
    var desiredDates: MutableList<LocalDate> = desiredDates
        protected set
}
```

- The `@CollectionTable` annotation is required. In the above implementation, the table storing multiple values is `apply_desired_date`, with the join column designated as `apply_id`.
- The corresponding DDL for this entity can be approximated as follows:

```sql
create table apply (
    id bigint not null auto_increment,
    user_id bigint not null,
    primary key (id)
);
create table apply_desired_date (
    apply_id bigint not null,
    desired_dates date not null
);
```

### Rationale for Utilizing `@ElementCollection`

- Occasionally, scenarios arise requiring storage of multiple simple values (Int, String, LocalDate types, etc.) within an entity field. Multiple approaches exist:
    - Concatenating values with a defined delimiter (e.g., comma) and storing as a string in a single column
    - If the database supports JSON types (such as MySQL), storing in JSON format
    - Utilizing JPA's `@ElementCollection`
    - Employing JPA's one-to-many mapping
- In my specific case, multiple dates needed to be stored only when the entity possessed a particular status. If the requirements merely involved storage and retrieval with direct conversion, alternative approaches could have been considered. However, a batch process requiring notification when stored dates matched the current date necessitated consideration of query performance. Consequently, `@ElementCollection` was adopted as it appeared convenient for entity-level management while maintaining query efficiency.
- For fields not completely dependent on the entity or representing more than simple values, establishing many-to-one/one-to-many relationships or employing indirect reference patterns would be more appropriate.

### Error Encountered When Utilizing List Type

Kotlin's List represents an immutable type. MutableList must be employed when value modification is required. When utilizing a field annotated with `@ElementCollection`, I initially considered that "if completely new List assignment occurs, MutableList might be unnecessary," leading to List utilization, which generated the following error:

```
java.lang.UnsupportedOperationException
	at java.base/java.util.AbstractList.remove(AbstractList.java:167)
	at java.base/java.util.AbstractList$Itr.remove(AbstractList.java:387)
	at java.base/java.util.AbstractList.removeRange(AbstractList.java:598)
	at java.base/java.util.AbstractList.clear(AbstractList.java:243)
	at org.hibernate.type.CollectionType.replaceElements(CollectionType.java:580)
	at org.hibernate.type.CollectionType.replace(CollectionType.java:757)
	at org.hibernate.type.TypeHelper.replace(TypeHelper.java:168)
	...
	at jdk.proxy3/jdk.proxy3.$Proxy110.merge(Unknown Source)
	at org.springframework.data.jpa.repository.support.SimpleJpaRepository.save(SimpleJpaRepository.java:669)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:568)
```

JPA internally invoked AbstractList.remove(), which is unavailable for List type, resulting in UnsupportedOperationException.

Examination of the previously invoked CollectionType's `replaceElements()` method reveals iterative clearing of the target object followed by addition from the original object:

```
/**
	 * Replace the elements of a collection with the elements of another collection.
	 *
	 * @param original The 'source' of the replacement elements (where we copy from)
	 * @param target The target of the replacement elements (where we copy to)
	 * @param owner The owner of the collection being merged
	 * @param copyCache The map of elements already replaced.
	 * @param session The session from which the merge event originated.
	 * @return The merged collection.
	 */
	public Object replaceElements(
			Object original,
			Object target,
			Object owner,
			Map copyCache,
			SharedSessionContractImplementor session) {
		java.util.Collection result = ( java.util.Collection ) target;
		result.clear();

		// copy elements into newly empty target collection
		Type elemType = getElementType( session.getFactory() );
		Iterator iter = ( (java.util.Collection) original ).iterator();
		while ( iter.hasNext() ) {
			result.add( elemType.replace( iter.next(), null, session, owner, copyCache ) );
		}
/* ....omitted for brevity */

		return result;
	}
```

⇒ Conclusion: Collections that will not or must not be modified should utilize List; otherwise, MutableList must be employed. (An apparently self-evident statement upon reflection)

### Example Code Repository

[https://github.com/myangw/jpa-test](https://github.com/myangw/jpa-test)

Tests can be executed and verified through the `ApplyServiceTest` class.
