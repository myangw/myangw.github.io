---
title: "Toby's Spring Chapter 7: Application of Core Spring Technologies"
date: 2021-03-07T00:00:00+09:00
slug: "tobys-spring-chapter-7-application-of-core-technologies"
tags:
  - Spring
draft: false
ShowToc: true
TocOpen: false
---

This chapter applies Spring's three core technologies—IoC/DI, service abstraction, and AOP—to application development for creating novel functionality, thereby examining Spring's development philosophy, pursued values, and requirements for Spring users.

## 7.1 Separating SQL and DAO

- Final UserDao improvement: Extracting SQL from DAO
  - Runtime modifications to database tables, field names, or SQL statements necessitate DAO recompilation, proving impractical

### SQL Separation Methodologies

1. XML configuration-based separation: Define SQL as XML property values for DAO injection
2. SQL provision service: Create independent functionality providing SQL for DAO usage

The second approach proves superior, enabling SQL storage in various formats beyond Spring configuration files and facilitating runtime modifications.

## 7.2 Interface Separation and Self-Referencing Beans

Developing the SqlService interface implementation:

### XML File Mapping

- Utilize JAXB for XML-to-Java object conversion
- Initialization work should employ designated initialization methods (`@PostConstruct`) rather than constructors

### Interface Separation for Change Preparation

Separate concerns into independent responsibilities:
1. Reading SQL information from external resources
2. Maintaining retrieved SQL and providing upon necessity
3. SQL modification as required (addressed subsequently)

### Self-Referencing Bean Implementation

- Initiate by implementing three interfaces (SqlReader, SqlService, SqlRegistry) within single XmlSqlService class
- Self-referencing beans constitute initial attempts when transforming inflexible structures into flexible architectures

### Default Dependencies

- When specific dependency objects receive default usage, create beans possessing default dependency relationships
- Automatically applied absent external DI

## 7.3 Service Abstraction Application

### OXM Abstraction

- Service abstraction for XML-Java object mapping technologies
- Spring's Unmarshaller interface enables JAXB, Castor, et cetera substitution through bean configuration modification

### Resource Abstraction

- Spring's Resource interface provides unified access to resources at diverse locations (classpath, file system, HTTP)
- Resource types specified via string prefixes (classpath:, file:, http:)

## 7.4 Safe Feature Extension Through Interface Inheritance

### Interface Inheritance

- Extend interfaces through inheritance rather than creating multiple interfaces
- Example: Extend SqlRegistry with UpdatableSqlRegistry for SQL modification functionality

## 7.5 Implementing Diverse Implementations with DI

### ConcurrentHashMap-Based Implementation

- Employ synchronized HashMap optimized for concurrent data manipulation
- Thread-safe with guaranteed performance

### Embedded Database Implementation

- Utilize embedded databases for substantial data quantities with frequent queries and modifications
- Spring provides convenient embedded database builders

### Transaction Application

- Multiple SQL batch modifications necessitate transactional execution
- Employ TransactionTemplate for simple transactions

## 7.6 Spring 3.1 DI

### Java Code-Based Bean Configuration

- Replace XML with `@Configuration` classes
- Employ `@Bean` methods for bean definitions

### Bean Scanning and Autowiring

- `@Autowired`: Container locates injectable beans by type/name
- `@Component`: Designates classes for automatic bean registration
- `@ComponentScan`: Enables bean scanning functionality

### Context Separation and @Import

- Separate configuration classes by characteristics
- `@Import`: Consolidate modularized configurations

### Profiles

- Define bean configurations varying by execution environment
- Specify active profiles at runtime

### Property Sources

- Store environment-dependent settings in property files
- `@PropertySource`: Register property files
- `@Value`: Direct property value DI

### Bean Configuration Reusability

- Enable configuration reusability through `@Enable*` annotations
- Example: Create `@EnableSqlService` for SqlServiceContext inclusion

[Images from original preserved in directory]
