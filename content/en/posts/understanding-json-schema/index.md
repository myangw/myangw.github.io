---
title: "Understanding JSON Schema"
date: 2023-07-16T00:00:00+09:00
slug: "understanding-json-schema"
tags:
  - json-schema
draft: false
ShowToc: true
TocOpen: false
---

## What is JSON Schema?

> **JSON Schema** is a declarative language that allows you to **annotate** and **validate** JSON documents.
>
(annotate: to add notes / validate: to verify)

⇒ As the name suggests, it's a schema for JSON, used to describe and validate items.

- The sender of data can describe the data and define types, and the receiver can validate the data through the schema before using it.
- Simply put, it can be described as a specification created to reduce various difficulties when exchanging data in JSON. For example, you receive data in JSON from an API or message queue: `{ id: "34", … }`. How should we interpret this? Is it always a string? Could it have been sent incorrectly? If I set up parsing to receive it as a String, but one day it comes as an Integer, how should I handle it? To solve these problems, you can clearly specify the data structure through a schema and ensure data quality.
- Because there's a standard specification on 'how to define the schema', you can automate the reading and sending according to the standard.

Let's see what it looks like.

- Assume we're sending an object called product in JSON.

```json
{
  "productId": 1,
}
```

- The JSON schema for the above JSON can be expressed as follows.

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

- The `$schema` field indicates which version of the draft of the json-schema standard is being used.
- The `$id` field defines the URI where this schema is located.
- `title`, `description` are fields for documentation.
- Inside the `properties` field, you can express detailed definitions about properties. Type, whether it's required, minimum value the field can have, etc.

### How to Communicate

I was wondering whether the schema needs to be included in the original JSON document or sent separately, but it turns out the schema is uploaded to a specific URI and used. Looking at the example URI on the official website makes it immediately clear. https://json-schema.org/learn/examples/calendar.schema.json

> JSON Schema is hypermedia ready, and ideal for annotating your existing JSON-based HTTP API. JSON Schema documents are identified by URIs, which can be used in HTTP Link headers, and inside JSON Schema documents to allow recursive definitions.
>

+) When communicating via Kafka, you can use Confluent's [schema registry](https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/serdes-json.html). The producer uploads the schema to the registry, and the consumer interprets the data according to the schema obtained from the registry.

## Implementations

There are quite a few implementations by language listed in the [official documentation](https://json-schema.org/implementations.html).

Since I plan to use it in a Java project, after clicking through and researching them all:

- Has the most stars but documentation and release status aren't the most recent: https://github.com/java-json-tools/json-schema-validator
- Has quite a few stars and is currently being actively released: https://github.com/networknt/json-schema-validator

I think using one of these two would be good.

I briefly tested networknt/json-schema-validator, which is a recent release that claims to be high-performance compared to other implementations. I referred to the [quick-start documentation](https://github.com/networknt/json-schema-validator/blob/master/doc/quickstart.md).

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

⇒ Test passes. Since the id type is number, a ValidationMessage is created in errors.

If you change the id type to number, errors becomes an empty set:

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

- Official site https://json-schema.org/
