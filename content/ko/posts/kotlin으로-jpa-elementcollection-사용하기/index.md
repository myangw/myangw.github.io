---
title: "Kotlin으로 JPA @ElementCollection 사용하기"
date: 2023-02-26T00:00:00+09:00
slug: "Kotlin으로 JPA @ElementCollection 사용하기"
tags:
  - JPA
draft: false
ShowToc: true
TocOpen: false
---

최근 실무에서 오랜만에 JPA의  `@ElementCollection` 기능을 사용하게되었다. 많이 까먹은데다 정리해둔 것도 없어 처음 쓸때도 여러 번 검색하며 고민했고, 이런저런 에러도 마주하게 되어 간단히 정리해보려 한다. 

### `@ElementCollection` 이란?

- JPA의 `@ElementCollection`은 값 타입 collection을 매핑할 때 사용할 수 있는 기능이다.
- @Entity가 아닌 기본 타입이나 Embeddable 클래스로 정의된 컬렉션을 참조할 때 사용한다.
- db상으로는 별도의 테이블을 생성하게 된다.

간단한 예시로 유저의 ‘신청’이라는 엔티티가 있고, ‘희망하는 날짜’를 여러개 체크할 수 있다고 가정하면 아래와 같이 구성해볼 수 있다.

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

- `@CollectionTable` 이라는 어노테이션이 함께 필요하다. 위 코드에서 여러개의 값을 저장하는 테이블은 `apply_desired_date` 이고, join은 `apply_id` 라는 컬럼으로 하게 된다.
- 위 엔티티에 대한 DDL은 대략 아래처럼 쓸 수 있다.

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

### 왜 `@ElementCollection` 을 쓰게 되었는가

- 가끔 엔티티의 필드에 여러개의 단순한 value(Int, String, LocalDate 타입 등)를 저장해야하는 상황이 생긴다. 여러 가지 방법들이 있을 수 있다.
    - 정해진 구분자(comma(,) 등)로 연결해서 string으로 하나의 컬럼에 저장
    - mysql과 같이 json타입을 허용하는 db라면 json형식으로 저장하는 방법
    - JPA의 `@ElementCollection` 사용
    - JPA의 일대다 매핑 사용
- 나의 경우 엔티티가 특정 status를 가질 때만 사용되는 여러개의 날짜를 저장해야했다. 단순히 저장하고 그대로 변환해서 조회하는 로직만 필요했다면 위의 방식을 좀더 생각해볼 수 있었을텐데, 저장된 날짜들에 대해 조회해와서 오늘 날짜와 같으면 알림을 보내는 배치가 필요했다. ⇒ 조회 성능을 고려했을 때 + 엔티티 상에서 관리하기도 편할 것 같아서 사용하게 되었다.
- 엔티티에 완전히 종속적인 필드 + 단순한 value가 아니라면 다대일/일대다 관계로 relation을 걸거나 간접 참조 방식을 사용하는게 좋을 것 같다.

### List 타입을 사용하다가 만난 에러

Kotlin의 List는 Immutable한 타입이다. 값을 변경해야한다면 MutableList를 사용한다. `@ElementCollection` 을 사용한 필드를 수정할 때 ‘완전히 새로운 List를 할당한다면 MutableList를 쓰지 않아도 괜찮지 않을까?’ 라고 무심코 생각하며 List를 사용했더니 아래와 같은 에러가 생겼다. 

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

JPA 내부적으로는 AbstractList.remove()를 호출했는데 List타입에는 없는 메서드라 UnsupportedOperationException이 발생한 것.

그 전에 호출된 아래의 CollectionType의 `replaceElements()` 를 보면 iterator를 돌며 한땀한땀 target객체를 비운 뒤 original 객체에 add 하는 것을 확인할 수 있다. 

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
/* ....너무 길어서 생략 */

		return result;
	}
```

⇒ 수정될일 없는/수정되면 안되는 Collection이라면 List를 사용하고, 그렇지 않은 경우에는 MutableList를 사용해야한다는 결론을 얻었다. (쓰고보니 너무나 당연한 문장)

### 예제 코드 repository

[https://github.com/myangw/jpa-test](https://github.com/myangw/jpa-test)

`ApplyServiceTest` 클래스에서 테스트를 돌려보며 확인 가능하다.