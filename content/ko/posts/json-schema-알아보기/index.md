---
title: "json schema 알아보기"
date: 2023-07-16T00:00:00+09:00
slug: "json schema 알아보기"
tags:
  - json-schema
draft: false
ShowToc: true
TocOpen: false
---

## Json schema란?

> **JSON Schema** is a declarative language that allows you to **annotate** and **validate** JSON documents.
> 
(annotate: 주석을 달다 / validate: 검증하다)

⇒ 말그대로 JSON에 대한 스키마이며, 항목들을 설명하고 검증하는데에 사용된다.

- 데이터를 보내는 쪽에서는 데이터에 대한 설명, 타입에 대한 정의 등을 할 수 있고, 받는 쪽에서는 스키마를 통해 데이터를 검증해서 사용 가능하다.
- 쉽게 표현하면, json으로 데이터를 주고받을 때의 여러 고충(?)들을 줄이기 위해 만든 명세 라고 할 수 있을것 같다. 예를 들어 api, 메시지 큐 등으로부터 json으로 전달받은 데이터가 `{ id: “34”, … }` 다. 이걸 어떻게 바라봐야할까? 늘 문자열인가? 혹시 잘못 보낸건 아닐까? 파싱을 String으로 받도록 했는데 어느날 Integer로 오면 어떻게 처리를 해야할까?  이런 문제들을 해결하고자 명확하게 스키마를 통해 데이터에 대한 구조를 명시적으로 약속하여 데이터의 품질을 보장할 수 있다.
- 이 ‘스키마를 어떻게 정의할 것인가’에 대해서 표준 명세가 있기 때문에, 표준에 따라 읽어들이고 보내는 부분을 자동화할 수 있다.

그럼 어떻게 생겼는지 살펴보자.

- product라고 부르는 객체를 json으로 보낸다고 가정해보자.

```json
{
  "productId": 1,
}
```

- 위의 json에 대한 json schema는 아래와 같이 표현할 수 있다.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/product.schema.json",
  "title": "Product",
  "description": "A product from Acme's catalog",
  "type": "object",
  "properties": {
    "productId": {
      "description": "The unique identifier for a product",
      "type": "integer",
	  "exclusiveMinimum": 1
    }
  },
  "required": [ "productId" ]
}
```

- `$schema` 필드는 json-schema의 표준 중 어떤 버전의 draft를 쓰는지를 나타낸다.
- `$id` 필드는 이 스키마가 있는 uri를 정의한다.
- `title`, `description`은 문서화를 위한 필드.
- `properties` 필드 안에서 프로퍼티에 대한 상세한 정의를 나타낼 수 있다. 타입, 필수값인지의 여부, 해당 필드가 가질 수 있는 최소값 등등.

### 어떻게 통신하는가

스키마를 원래의 json document에 포함시켜야한다는건지, 따로 보낸다는건지? 가 궁금했는데, 스키마를 특정 URI에 올려놓고 사용하는 방식이었다. 공식 사이트에 있는 예시 URI를 보면 금방 이해가 된다. https://json-schema.org/learn/examples/calendar.schema.json 

> JSON Schema is hypermedia ready, and ideal for annotating your existing JSON-based HTTP API. JSON Schema documents are identified by URIs, which can be used in HTTP Link headers, and inside JSON Schema documents to allow recursive definitions.
> 

+) kafka로 통신할때는 confluent의 [schema registry](https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/serdes-json.html)를 사용하면 될 것 같다. producer는 registry에 스키마를 업로드해두고,  consumer는 registry를 통해 얻은 스키마에 따라 데이터를 해석하는 방법.

## 구현체

[공식문서](https://json-schema.org/implementations.html)에 안내된 구현체들은 언어별로 꽤 많다. 

Java 프로젝트에 사용할 예정이라 다 클릭해보고 찾아본 결과:

- star가 가장 많지만 문서와 릴리즈 상태가 최신은 아닌:  https://github.com/java-json-tools/json-schema-validator
- star가 꽤 많고 현재도 active하게 릴리즈되고있는:  https://github.com/networknt/json-schema-validator

요 두가지 중 하나를 쓰면 되지 않을까 싶다.

다른 구현체에 비해 고성능이라고 주장하는 최신 릴리즈의 networknt/json-schema-validator 를 간단히 테스트 해봤다. [quick-start 문서](https://github.com/networknt/json-schema-validator/blob/master/doc/quickstart.md)를 참고했다.

```java
@Test
public void test() throws IOException {
    JsonNode schemaNode = getJsonNodeFromStringContent(
            "{\"$schema\": \"http://json-schema.org/draft-06/schema#\", \"properties\": { \"id\": {\"type\": \"number\"}}}");
    JsonSchema schema = getJsonSchemaFromJsonNodeAutomaticVersion(schemaNode);

    schema.initializeValidators();

    JsonNode node = getJsonNodeFromStringContent("{\"id\": \"2\"}");
    Set<ValidationMessage> errors = schema.validate(node);
    assertEquals(1, errors.size());
}


protected JsonNode getJsonNodeFromStringContent(String content) throws IOException {
    return mapper.readTree(content);
}

protected JsonSchema getJsonSchemaFromJsonNodeAutomaticVersion(JsonNode jsonNode) {
    JsonSchemaFactory factory = JsonSchemaFactory.getInstance(SpecVersionDetector.detect(jsonNode));
    return factory.getSchema(jsonNode);
}
```

⇒ 테스트 통과. id의 타입은 number이기 때문에 errors에 ValidationMessage가 생긴다.

id 타입을 number로 바꿔주면 errors는 빈 set이 된다.: 

```java
@Test
public void test() throws IOException {
    JsonNode schemaNode = getJsonNodeFromStringContent(
            "{\"$schema\": \"http://json-schema.org/draft-06/schema#\", \"properties\": { \"id\": {\"type\": \"number\"}}}");
    JsonSchema schema = getJsonSchemaFromJsonNodeAutomaticVersion(schemaNode);

    schema.initializeValidators();

    // JsonNode node = getJsonNodeFromStringContent("{\"id\": \"2\"}");
    // Set<ValidationMessage> errors = schema.validate(node);
    // assertEquals(1, errors.size());
	JsonNode node = getJsonNodeFromStringContent("{\"id\": 2 }");
    Set<ValidationMessage> errors = schema.validate(node);
    assertEquals(0, errors.size());
}
```

### Reference

- 공식 사이트 https://json-schema.org/
