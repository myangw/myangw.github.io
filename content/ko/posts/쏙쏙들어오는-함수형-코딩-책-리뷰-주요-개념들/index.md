---
title: "쏙쏙들어오는 함수형 코딩 책 리뷰 & 주요 개념들"
date: 2022-10-30T00:00:00+09:00
slug: "쏙쏙들어오는 함수형 코딩 책 리뷰 & 주요 개념들"
tags:
  - 함수형프로그래밍
draft: false
ShowToc: true
TocOpen: false
---

## 쏙쏙들어오는 함수형 코딩 책

장장 564p.나 되는 '쏙쏙 들어오는 함수형 코딩(에릭 노먼드 저)'책의 1회독을 끝냈다. 함께 스터디한 팀원들이 없었다면 정말 쉽지 않았을 여정. 그리고 이 책은 정말 친절하다. 함수형 코딩이라는 개념을 처음 접하는 사람들을 대상으로 쓰여진 책이고 중간중간 나오는 연습문제와 챕터 마지막의 결론, 다음 챕터에서의 반복 등으로 어렵지않게 학습할 수 있다. 우리 스터디에서는 연습문제를 스터디 시간에 같이 풀고 토론했는데 그 시간이 더 이해를 높이는데 도움이 되었던 것 같다.

책의 예제는 자바스크립트로 되어있지만, 저자는 이 책이 자바스크립트 책이 아니라고 재차 강조한다. 아마 다른 함수형 언어를 안다면 책을 잘 따라갈 수 있을 듯 하다. 


## 책의 주요 개념들

### 함수형 프로그래밍(Functional Programming. 이하 FP)이란…

책을 읽기 전까지 나의 나이브한 생각은 ‘부수효과를 만들지 않는 순수함수로 프로그래밍하는 패러다임 ?.?’ 정도였다. 위키피디아의 정의도 거의 비슷하다 :  `수학함수를 사용하고 부수효과를 피하는 것이 특징인 프로그래밍 패러다임`  그러나!! 저자는 일반적인 FP의 정의대로라면 이메일 전송도 하지 못할것이라고 지적하며, 부수효과를 아얘 만들지 않는게 아니라 잘 다룰 수 있는게 FP라고 말한다. 

책에서 다루는 함수형 사고의 가장 중요한 두가지 개념은 `액션과 계산, 데이터를 구분해서 생각하는 것`, 그리고 `일급추상` 이다. 



### 액션, 계산, 데이터 그리고 불변성을 지키는 원칙

- **액션, 계산, 데이터를 구분하고 더 좋은 코드를 위해서는 최대한 액션에서 계산을 분리하고 계산에서 데이터를 분리 해야한다.**
    - 액션 : 부수효과가 있는 함수. 실행시점과 횟수에 의존한다. ex. 이메일 보내기, db에서 읽어오기
    - 계산: 부수효과가 없는 순수함수.
    - 데이터: 이벤트에 대한 사실.  

- **액션, 계산, 데이터를 구분하는 것이 왜 중요한가?**
    
    ```javascript
    // 계산 구분 전
    var subscribers = ["myang", "soo", "sh"]
    function sendMessagesToSubscribers() {
    	for (var i = 0; i < subscribers.length; i++) {
    		if (getCouponRank(subscribers[i]) == "A") {
    			var message = {
    				title: "title for A grade customers" 
    				body: "You got a best deal: ~~"
    			};  // message 객체는 데이터다.
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
    
    // 계산 구분 후
    function sendMessagesToSubscribers(subscribers) {
    	var messages = messagesForSubscribers(subscribers);
    	for (var i = 0; i < subscribers.length; i++) {
    		sendMessage(message[i]);
    	}
    }
    
    function messagesForSubscribers(subscribers) { // 계산
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
    
    - 액션을 계산으로 바꾸면 재사용, 유지보수, 테스트하기 쉽다.
    - 계산을 조합하여 더 큰 계산을 만들 수 있다.
    - 계산은 동시에 실행되는 것, 실행 맥락, 실행 횟수를 걱정하지 않아도 된다.  

- **어떻게 액션을 계산으로 만들 수 있나**
    - 함수에 암묵적 입력(ex. 전역변수를 읽는 것)과 암묵적 출력(ex. console.log)이 있으면 액션.
        - 어떤 함수가 암묵적 입력과 출력을 가진다면, 그 함수와 연결된 부분의 동작에 의존하고 강하게 결합됨. 다른 곳에서 사용할 수 없게 된다.
    - 암묵적 입력은 parameter로, 암묵적 출력은 return 값으로 나타내면 계산이 된다.
    - 이 암묵적 입출력을 없애는 과정에서 불변성 구현이 필요하다.
        - 변경 가능한 데이터를 읽는 것은 액션(읽을 때마다 다른 값을 읽을 수 있으므로)이지만, 불변 데이터 구조를 읽는 것은 계산이 된다.
        - Haskell, Clojure 등의 함수형 프로그래밍 언어는 언어 자체에서 불변성을 구현하고 있다. 그러나 자바스크립트는 직접 구현해야한다.
        - 불변성을 유지하기 위해 적용 가능한 원칙 1) copy-on-write: 어떤 값의 복사본을 만들고, 직접 값을 바꾸지 않는 것.
            
            ```javascript
            // 인자로 전달한 배열을 직접 변경하는 것은 액션이다. (배열이 바뀌는 부수효과가 발생)
            
            var cart = [...] // 전역변수
            remove_item_by_name(cart, 'rubber_duck');
            
            function remove_item_by_name(cart, name) {
            	var idx = null;
            	for(var i = 0; i < cart.length; i++) {
            		if(cart[i].name === name) {
            			idx = i;
            		}
            	if (idx !== null) {
            		cart.splice(idx, 1); // 전역변수를 수정
            	}
            }
            ```
            
            ```javascript
            // copy-on-write 적용하여 계산으로 바꾸기
            
            function remove_item_by_name(cart, name) {
            	var new_cart = cart.slice(); // 1. 복사본 만들기
            	for(var i = 0; i < new_cart.length; i++) {
            		if(new_cart[i].name === name) {
            			idx = i;
            		}
            	if (idx !== null) {
            		new_cart.splice(idx, 1); // 2. 복사본 변경하기
            	}
            	return new_cart; // 3. 복사본 리턴하기
            }
            ```
            
        - 불변성을 유지하기 위해 적용 가능한 원칙 2) 방어적 복사: 불변성이 지켜지는 안전지대의 바깥으로 들어오고 나가는 데이터의 복사본을 만들기
            
            
            - 바꿀 수 없는 레거시 코드 또는 라이브러리의 함수를 사용해야할 때, 안전지대 바깥과 상호작용 하게 된다.  
            - 이 때 deep copy로 nested data를 복사해야함
            - deep copy는 비용이 많이 듬. 안전지대 안에서는 copy-on-write로 충분하다.
            
            ```javascript
            function black_friday_promotion(cart) {
            	 // 통제 바깥의 코드. 무슨 일이 일어나는지 알 수 없음. cart를 변경할 수도 있음
            }
            
            function add_item_to_cart(name, price) {
            	// ...
            	var cart_copy = deepCopy(cart); // 데이터가 안전지대에서 나갈 때 복사
            	black_friday_promotion(cart_copy);
            	cart = deepCopy(cart_copy); // 안전지대로 데이터가 들어올 때 복사
            }
            ```
    
        
        ** 이렇게 코드짤때마다 신경쓰면서 일일이 다 copy를 해야할까? 에 대한 대안은 immutable.js 같은 라이브러리 사용이 아닐까 싶다. 코틀린의 경우 immutable collection을 쓰는것
        


### 일급 추상

- 일급 객체
    - 1) 변수에 할당할 수 있고 2) 함수의 인자로 넘길 수 있고 3)함수의 리턴값으로 받을 수 있고 4) 배열/객체에 담을 수 있으면 일급(first-class)이라고 한다.
    - 자바스크립트에서는 함수도 일급 객체다.
- 고차함수
    - 함수를 인자로 받는 함수
    - 함수를 리턴하는 함수(커링)도 고차함수에 포함되는 개념
        - 함수를 리턴하기때문에 `blablaFunction(a)(b)` 같은 문법이 가능하다. `blablaFunction(a)`의 결과가 또 함수이기 때문에 `blablaReturnFunction(b)`가 되어서 실행되는 식..
    - 고차함수는 뭐가 좋을까?
        - 코드를 추상화할 수 있다.
        - ‘함수 본문을 콜백으로 바꾸기’와 같은 암묵적 출력을 제거하는 리팩토링이 가능해진다.
            
            ```javascript
            // 리팩토링 전
            function calc_total(cart) {
            	// ...
            	update_total_dom(total);
            }
            
            // 리팩토링 후
            function calc_total(cart, callback) {
            	// ...
            	callback(total);
            }
            ```
            

- 함수형 도구들: map(), filter(), reduce()
    - reduce 함수 특이점!
        - 단순히 누산하는데에만 쓰이지 않고, 여러 쓰임새가 있다.
            - list 형태인 경우 되돌리기(실행취소)를 구현하려면 reduce한거에서 마지막 항목만 빼면 된다.
            - 초기값이 있고 사용자 입력이 순서대로 리스트에 있다면, reduce()로 모든 값을 합쳐 현재 상태를 만들 수 있다.
            - 특정 시점의 시스템 상태 알기(그 시점까지의 history를 reduce하면 되니까)
        - ⇒ 이벤트 소싱과 비슷한 개념.
        - filter, map도 결국 reduce로 만들 수 있다.
        
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
        



위의 개념들 외에도 타임라인 커팅, 계층형 설계, 동시성을 다루는 부분들도 나오는데 다 담지는 못하겠다…. 동시성 관련은 조금더 공부해서 따로 글을 써보고 싶다. 

입문서라 길게 공부했음에도 이 책만으로 함수형 프로그래밍은 맛보기만 한 기분이다. 다음 책은 무엇으로..?