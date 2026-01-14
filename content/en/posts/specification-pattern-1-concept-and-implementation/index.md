---
title: "Specification Pattern (1) Concept and Implementation"
date: 2024-10-08T00:00:00+09:00
slug: "specification-pattern-1-concept-and-implementation"
summary: "Express domain rules simply and explicitly"
tags:
  - DDD
  - patterns
draft: false
ShowToc: true
TocOpen: false
---

## intro

The specification pattern is something my team has studied and used effectively in various projects to handle changing policies/rules. In this article, I'll introduce what the specification pattern is and how things can change before and after applying it.


## What is the Specification Pattern?

The specification pattern in object-oriented programming allows you to concisely express specific rules about a domain. It separates **rules** from **conditional logic implemented inside the domain**, making the rules explicit. If the conditions are simple, there's no need to separate them, but as business requirements are added, rules can be varied and combined in many ways beyond the original purpose of entities or value objects. At this point, you create a specification separated as a predicate that determines whether an entity or value object meets specific criteria.

```java
interface Specification {
	boolean isSatisfiedBy(Object anObject);
}
```

To express rules, you implement multiple Specifications and logically combine predicates with operators like and, or, not to indicate whether an object meets certain criteria.

What I mean by combining predicates - using performance entry policy as an example

```java
// isEntryAllowed = (hasTicket) and not(hasPerformanceStarted)
boolean isEntryAllowed = hasTicket(customer).and(not(hasPerformanceStarted()));
```

→ Like `isEntryAllowed`, it means representing each detailed condition as a combination of concrete Specifications that implement the Specification interface.

.

## Example

Just explaining might not be very impactful. Let me give an example of how specification becomes useful in a specific situation. (I took an example from the 'Domain-Driven Design' book and added some flesh to it.)

Assume in a payment domain that issues invoices, you check customer delinquency information and send emails. There are two conditions for determining whether to send an email:
 * When today's date exceeds the invoice due date + grace period combined
 * When the unpaid amount exceeds $100

### Before Applying Specification

When creating a method to judge conditions inside domain objects without using the specification pattern, you can write code like below.

```java
class Invoice {
    private LocalDate dueDate;
    private Customer customer;
    private Money totalAmount;

    boolean isThresholdReached(Money thresholdAmount) {
        return totalAmount.greaterThanOrEqual(thresholdAmount);
    }

    boolean isOverdue(LocalDate currentDate) {
        int gracePeriod = customer.getPaymentGracePeriod();
        LocalDate firmDeadline = dueDate.plusDays(gracePeriod);
        return currentDate.isAfter(firmDeadline);
    }

}
```

Client code for email sending that uses domain logic is written with conditional statements for the judgment conditions.

```java
if (invoice.isOverdue(LocalDate.now()) && invoice.isThresholdReached(Money.of(100))) {
  send(invoice);
}
```

So far it doesn't look too bad. But what if new requirements are added after deploying to production?
* Z-type Invoices should not send emails

Add a method to Invoice and add a judgment condition. ~~I added line breaks for readability.~~

```java
if (invoice.isOverdue(LocalDate.now()) &&
		invoice.isThresholdReached(Money.of(100)) &&
		invoice.isNotZType()
		) {
  send(invoice);
}
```

If another requirement comes in a few days later...?
* Among delinquent users, customers with delinquent amounts exceeding $4000 should receive emails with a different template.

It can be implemented in various ways, but roughly it would be code like below.
```java
if (invoice.isOverdue(LocalDate.now()) &&
        invoice.isThresholdReached(Money.of(100)) &&
        invoice.isNotZType()
) {
    send(invoice, TEMPLATE_NORMAL);
} else if (invoice.isOverdue(LocalDate.now()) &&
        invoice.isThresholdReached(Money.of(4000)) &&
        invoice.isNotZType()
) {
    send(invoice, TEMPLATE_OVER_4000);
}
```

#
With just two requirement additions, the code readability has already dropped significantly. As other requirements increase and conditions multiply, you have to think about where to insert them while following existing code logic. Invoice object methods will have more methods for conditions to determine rules than the Invoice object's original responsibility.

### Applying Specification

How does it change when using specification?

Requirements
* When today's date exceeds the invoice due date + grace period combined
* When the unpaid amount exceeds $100

Create Specification implementations for each.

```java
// (Specification naming was too long so I shortened it to Spec)

interface InvoiceSpec {
	boolean isSatisfiedBy(Invoice candidate);
}

class DelinquentInvoiceSpec implements InvoiceSpec {
    private LocalDate currentDate;

    public DelinquentInvoiceSpec(LocalDate currentDate) {
        this.currentDate = currentDate;
    }

    @Override
    public boolean isSatisfiedBy(Invoice candidate) {
        int gracePeriod = candidate.customer().getPaymentGracePeriod();
        LocalDate firmDeadline = candidate.dueDate().plusDays(gracePeriod);
        return currentDate.isAfter(firmDeadline);
    }
}

class BigInvoiceSpec implements InvoiceSpec {
    private Money thresholdAmount;

    public BigInvoiceSpec(Money thresholdAmount) {
        this.thresholdAmount = thresholdAmount;
    }

    @Override
    public boolean isSatisfiedBy(Invoice candidate) {
        return candidate.getTotalAmount().greaterThanOrEqual(thresholdAmount);
    }
}
```

#
And to combine the two conditions with and, create an And Specification implementation.

```java
public static class AndSpec implements InvoiceSpec {
    private final InvoiceSpec spec1;
    private final InvoiceSpec spec2;

    public AndSpec(InvoiceSpec spec1, InvoiceSpec spec2) {
        this.spec1 = spec1;
        this.spec2 = spec2;
    }

    @Override
    public boolean isSatisfiedBy(Invoice candidate) {
        return spec1.isSatisfiedBy(candidate) && spec2.isSatisfiedBy(candidate);
    }

    public static InvoiceSpec and(InvoiceSpec left, InvoiceSpec right) {
        return new AndSpec(left, right);
    }
}
```

#
Client code for sending emails is expressed as follows.

```java
static final InvoiceSpec DELINQUENT_SPEC = new DelinquentInvoiceSpec(LocalDate.now());
static final InvoiceSpec BIG_INVOICE_SPEC = new BigInvoiceSpec(Money.of(100));
static final InvoiceSpec EMAIL_SEND_SPEC = and(DELINQUENT_SPEC, BIG_INVOICE_SPEC);

private void send(Invoice invoice) {
	if (EMAIL_SEND_SPEC.isSatisfiedBy(invoice)) {
	  send(invoice);
	}
}
```

#
If you represent and like an infix operator, it can be expressed more like a sentence in human language. This is possible by implementing a default method in the interface.

```java
public interface InvoiceSpec {
    boolean isSatisfiedBy(Invoice candidate);

    default InvoiceSpec and(InvoiceSpec right) {
        return new Specs.AndSpec(this, right);
    }
}

InvoiceSpec EMAIL_SEND_SPEC = DELINQUENT_SPEC.and(BIG_INVOICE_SPEC);
```

#
When adding more requirements here, the code can be written like this. ~~Please overlook the variable names~~
* Z-type invoices should not send emails
* Among delinquent users, customers with delinquent amounts exceeding $4000 should receive emails with a different template

```java
static final InvoiceSpec DELINQUENT_SPEC = new DelinquentInvoiceSpec(LocalDate.now());
static final InvoiceSpec Z_TYPE_SPEC = new TypeSpec("Z");
static final InvoiceSpec BIG_INVOICE_SPEC = new BigInvoiceSpec(Money.of(100));
static final InvoiceSpec BIG_INVOICE_SPEC_4000 = new BigInvoiceSpec(Money.of(4000));

static final InvoiceSpec EMAIL_SEND_NORMAL_SPEC = DELINQUENT_SPEC.and(BIG_INVOICE_SPEC).and(not(Z_TYPE_SPEC));
static final InvoiceSpec EMAIL_SEND_4000_SPEC = DELINQUENT_SPEC.and(BIG_INVOICE_SPEC_4000).and(not(Z_TYPE_SPEC));

private void send(Invoice invoice) {
    if (EMAIL_SEND_NORMAL_SPEC.isSatisfiedBy(invoice)) {
        send(invoice, TEMPLATE_NORMAL);
    }
    if (EMAIL_SEND_4000_SPEC.isSatisfiedBy(invoice)) {
        send(invoice, TEMPLATE_4000);
    }
}
```

#
When requirements are added, you can create them by reusing and combining existing Specifications. If you refactor the above code a bit more to make the client depend only on the InvoiceSpec interface, it becomes simpler and easier to write test code. For the various conditions declared as constants, you can separate them into objects that represent conditions and the results according to conditions.

#

  ![/spec-diagram.png](spec-diagram.png)

.


## Conclusion
Specification is not a pattern commonly introduced in the Gang of Four (GoF) design pattern book like composite or singleton patterns, so it was unfamiliar when I first heard of it. It's a pattern developed by Martin Fowler and Eric Evans, described in chapters 9 and 10 of the 'Domain-Driven Design (Eric Evans)' book and in Martin Fowler's paper. Fowler introduces this as both a design pattern and an analysis pattern (a way of capturing how people think about domains).

I'll cover more detailed examples of the pattern from the 'Domain-Driven Design' book and actual uses in the next article.


## References
- [Eric Evans, 'Domain-Driven Design'](https://product.kyobobook.co.kr/detail/S000001514402)
- [Martin Fowler, Specification](https://www.martinfowler.com/apsupp/spec.pdf)


- [Example code github](https://github.com/myangw/specification-example)
