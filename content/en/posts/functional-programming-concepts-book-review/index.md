---
title: "Functional Programming Concepts: A Comprehensive Book Review and Analysis of Core Principles"
date: 2022-10-30T00:00:00+09:00
slug: "functional-programming-concepts-book-review"
tags:
  - functional programming
draft: false
ShowToc: true
TocOpen: false
---

## Grokking Simplicity: Taming Complex Software with Functional Thinking

I have completed the first reading of "Grokking Simplicity" by Eric Normand, an extensive 564-page volume. This journey would have been considerably more challenging without the collaborative study group participants. This text demonstrates exceptional pedagogical quality. Authored specifically for individuals encountering functional programming concepts for the first time, it facilitates accessible learning through interspersed practice problems, chapter conclusions, and recapitulation in subsequent chapters. Our study group collaboratively solved practice problems during sessions and engaged in discussions, which significantly enhanced comprehension.

While the book's examples utilize JavaScript, the author repeatedly emphasizes that this is not a JavaScript-specific text. Familiarity with alternative functional programming languages would likely enable successful engagement with the content.


## Core Concepts Presented in the Text

### Defining Functional Programming (hereafter abbreviated as FP)

Prior to reading this text, my naive understanding was: "A programming paradigm characterized by pure functions without side effects?" Wikipedia's definition is approximately similar: "A programming paradigm characterized by the use of mathematical functions and avoidance of side effects." However, the author contends that according to conventional FP definitions, even email transmission would be impossible, asserting that FP is not about completely eliminating side effects but rather managing them effectively.

The two most critical concepts in functional thinking presented in this text are: "distinguishing between actions, calculations, and data," and "first-class abstractions."


### Actions, Calculations, Data, and Principles for Maintaining Immutability

- **Distinguishing between actions, calculations, and data, and for superior code quality, maximally separating calculations from actions and data from calculations is essential.**
    - Actions: Functions with side effects. Dependent on execution timing and frequency. Examples: sending email, database reads
    - Calculations: Pure functions without side effects.
    - Data: Facts regarding events.

- **Why is distinguishing actions, calculations, and data important?**

    ```javascript
    // Before calculation separation
    var subscribers = ["myang", "soo", "sh"]
    function sendMessagesToSubscribers() {
    	for (var i = 0; i < subscribers.length; i++) {
    		if (getCouponRank(subscribers[i]) == "A") {
    			var message = {
    				title: "title for A grade customers"
    				body: "You got a best deal: ~~"
    			};  // message object is data
    			sendMessage(message);
    		} else {
    			var message = {
    				title: "title for B grade customers"
    				body: "You got a bad deal: ~~"
    			};
    			sendMessage(message);
    		}
    	}
    }

    // After calculation separation
    function sendMessagesToSubscribers(subscribers) {
    	var messages = messagesForSubscribers(subscribers);
    	for (var i = 0; i < subscribers.length; i++) {
    		sendMessage(message[i]);
    	}
    }

    function messagesForSubscribers(subscribers) { // calculation
    	return subscribers.map(subscribers, function(subscriber) {
    		return messageForSubscriber(subscriber);
    	});
    }

    function messageForSubscriber(subscriber) {
    	if (getCouponRank(subscribers[i]) == "A") {
            return {
                title: "title for A grade customers"
                body: "You got a best deal: ~~"
            };
        } else {
            return {
                title: "title for B grade customers"
                body: "You got a bad deal: ~~"
            };
        }
    }
    ```

    - Converting actions to calculations facilitates reuse, maintenance, and testing.
    - Calculations can be composed to construct larger calculations.
    - Calculations eliminate concerns regarding concurrent execution, execution context, and execution frequency.

- **How can actions be converted to calculations?**
    - Functions possessing implicit inputs (e.g., global variable reads) and implicit outputs (e.g., console.log) are actions.
        - Functions with implicit inputs and outputs depend on the behavior of connected components and are tightly coupled, precluding utilization elsewhere.
    - Converting implicit inputs to parameters and implicit outputs to return values transforms them into calculations.
    - Implementing immutability is necessary during this implicit input/output elimination process.
        - Reading mutable data is an action (different values may be read each time), whereas reading immutable data structures is a calculation.
        - Functional programming languages such as Haskell and Clojure implement immutability at the language level. However, JavaScript requires manual implementation.
        - Principle 1 for maintaining immutability: Copy-on-write: Creating copies of values without directly modifying them.

            ```javascript
            // Directly modifying the array passed as an argument is an action (side effect of array modification)

            var cart = [...] // global variable
            remove_item_by_name(cart, 'rubber_duck');

            function remove_item_by_name(cart, name) {
            	var idx = null;
            	for(var i = 0; i < cart.length; i++) {
            		if(cart[i].name === name) {
            			idx = i;
            		}
            	if (idx !== null) {
            		cart.splice(idx, 1); // modifying global variable
            	}
            }
            ```

            ```javascript
            // Applying copy-on-write to convert to calculation

            function remove_item_by_name(cart, name) {
            	var new_cart = cart.slice(); // 1. Create copy
            	for(var i = 0; i < new_cart.length; i++) {
            		if(new_cart[i].name === name) {
            			idx = i;
            		}
            	if (idx !== null) {
            		new_cart.splice(idx, 1); // 2. Modify copy
            	}
            	return new_cart; // 3. Return copy
            }
            ```

        - Principle 2 for maintaining immutability: Defensive copying: Creating copies of data entering and exiting the safe zone where immutability is maintained


            - When interacting with immutable legacy code or library functions, interaction with the external safe zone occurs.
            - Deep copying is required for nested data in such scenarios.
            - Deep copying incurs substantial cost. Copy-on-write suffices within the safe zone.

            ```javascript
            function black_friday_promotion(cart) {
            	 // Code beyond control. Unknown operations. May modify cart
            }

            function add_item_to_cart(name, price) {
            	// ...
            	var cart_copy = deepCopy(cart); // Copy when data exits safe zone
            	black_friday_promotion(cart_copy);
            	cart = deepCopy(cart_copy); // Copy when data enters safe zone
            }
            ```


        ** Must copying be meticulously performed for every coding instance? Alternatives include utilizing libraries such as immutable.js. For Kotlin, employing immutable collections represents an analogous approach.



### First-Class Abstractions

- First-class objects
    - Objects are first-class if they can be: 1) assigned to variables, 2) passed as function arguments, 3) returned as function values, and 4) stored in arrays/objects.
    - In JavaScript, functions are first-class objects.
- Higher-order functions
    - Functions that receive functions as arguments
    - Functions that return functions (currying) are also encompassed within higher-order function concepts
        - Since they return functions, syntax such as `blablaFunction(a)(b)` becomes possible. `blablaFunction(a)` results in another function, enabling execution as `blablaReturnFunction(b)`...
    - What advantages do higher-order functions provide?
        - Code abstraction capability.
        - Enables refactoring such as "replacing function body with callback" to eliminate implicit outputs.

            ```javascript
            // Before refactoring
            function calc_total(cart) {
            	// ...
            	update_total_dom(total);
            }

            // After refactoring
            function calc_total(cart, callback) {
            	// ...
            	callback(total);
            }
            ```


- Functional tools: map(), filter(), reduce()
    - Notable characteristics of the reduce function
        - Not solely employed for accumulation; possesses multiple applications.
            - For list formats, implementing undo (execution cancellation) merely requires removing the final item from the reduced result.
            - Given an initial value and sequentially ordered user input list, reduce() can aggregate all values to produce the current state.
            - Determining system state at specific points in time (by reducing history up to that point)
        - These concepts parallel event sourcing.
        - Filter and map can ultimately be constructed using reduce.

        ```javascript
        function filter(array, f) {
        	return reduce(array, [], function(ret, item) {
        		if (f(item)) {
        			ret.push(item);
        		}
        		return ret;
        	});
        }
        ```



Beyond the concepts enumerated above, the text addresses timeline cutting, stratified design, and concurrency management, though comprehensive coverage proves impractical... I aspire to compose a dedicated article on concurrency-related topics following additional study.

As an introductory text, despite extended study, I retain the impression of merely sampling functional programming. What should constitute the subsequent text...?
