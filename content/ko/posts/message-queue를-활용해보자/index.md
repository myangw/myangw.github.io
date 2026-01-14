---
title: "message queue를 활용해보자"
date: 2023-02-12T00:00:00+09:00
slug: "message queue를 활용해보자"
tags:
  - message queue
  - 메시지 큐
  - SQS
draft: false
ShowToc: true
TocOpen: false
---

분산시스템에서 많이 사용되는 메시지 큐 (message queue)에 대해 공부해봤다. 실무에서 필요한 상황들이 앞으로 더 많이 생길 것 같아서 보편적으로 어떤 상황에서 메시지큐 도입을 고려하고, 여러 구현체들 중 어떤 기술을 써야할지 등을 정리했다.

## 개념

- 특정 메시지가 최소 한번은 전달될 수 있도록 보장(보관된 메시지가 꺼낼때까지 안전히 보관된다는 특성, durability)하는 비동기 통신을 지원하는 컴포넌트이다.
- 기본 아키텍처는 producer(발행자)가 메시지를 생성하여 queue에 저장하고,  consumer/subscriber(소비자/구독자)가 queue로부터 메시지를 받아 동작을 수행하는 구조. queue는 여기서 메시지의 버퍼 역할을 한다.
    
    ![/Untitled.png](Untitled.png)
    
- 메시지 브로커 라고도 한다.
- producer와 consumer는 1:1 이 될 수도 있고, 1:N 관계일 수도 있다.

### 데이터베이스와의 비교

- 대부분의 메시지큐는 소비자에게 데이터 전달이 완료되면 자동으로 메시지를 삭제한다. 오랜기간 데이터를 저장하는 용도로는 사용하지 않는다.
- queue가 처리하는 메시지들의 양이 작다고 가정한다. 많은 메시지를 큐에 저장할수록 전체 처리량이 저하된다.

### 장점

- 비동기
    - producer는 queue에 메시지를 넣고 응답을 기다리지 않고 다른 일을 할 수 있다.
- 데이터 유실 방지 (높은 reliablility)
    - 흔히 생산자-소비자 간 통신을 위해 쓰는 HTTP 같은 직접 통신은 메시지 유실 가능성이 있고, 생산자와 소비자가 항상 온라인 상태라고 가정한다. 그러나 둘 중 하나의 서버가 죽는다면 메시지를 잃어버릴 가능성이 생긴다.
    - 그러나 큐를 쓰면 소비자쪽 서버에 장애가 발생하거나 접속이 되지 않는 상태일때도 쉽게 대처할 수 있게 된다.
        - 큐가 소비자에게 전달되지 않은 메시지 혹은 실패한 메시지의 경우 메시지를 삭제하지 않기 대문.
- 고가용성(HA, High Availability) 유지
- 장애 복원에 유리 : 시스템 일부에 장애가 발생하더라도 전체적으로 영향을 주지 않는 설계가 가능하다.
- 확장성
    - 시스템을 구성하는 요소들끼리 독립적으로 동작하게 되어서 추가 서버나 리소스를 시스템에 추가하기 쉽다.

### queue방식과 pub-sub(topic)방식

- queue
    - consumer가 메시지를 한번 consume하면 queue에서 삭제된다.
    - 부하에 따라 같은 메시지큐를 listening하는 consumer를 여러개 둘 수 있다.
- pub/sub
    - 특정 consumer를 정하지 않고, 어떤 Topic을 구독하는 **모든** 수신자에게 메시지를 보낸다.
    - 송신자 - 수신자 사이에도 결합이 낮아 높은 확장성을 제공한다.

### pub-sub 방식으로 여러 consumer가 메시지를 읽을 때 사용하는 주요 패턴

1. 로드밸런싱(load balancing)
    - 브로커가 consumer 중 하나를 임의로 지정해서 하나의 consumer에게만 메시지를 전달하는 패턴.
    - 메시지 처리 비용이 비싸서 처리를 병렬화 하기 위해 consumer를 추가하고싶을 때 유용하다.
2. 팬 아웃(fan-out)
    - 모든 consumer들에게 메시지가 전달된다. 여러 독립적인 consumer가 서로 간섭 없이 동일한 메시지를 받아 처리할 수 있다.

## 어떤 상황에서 쓰면 좋을까?

- 시스템간 느슨한 결합(loose coupling)이 필요한 상황
    - 예를 들어 ‘회원가입‘이나 ‘주문’과 같은 작업은 가입한 시점/주문한 시점에 트리거되어서 유저에게 완료되었다는 안내 메시지를 보내거나 쿠폰을 발급하는 등 여러 동작들을 수행하는 경우가 많다.
    - 메시지 큐를 사용한다면 ‘회원가입’ 이나 ‘주문’을 처리하는 서버가 producer, ‘안내 메시지 전송’, ‘쿠폰 발급’을 처리하는 서버가 consumer가 될 수 있다.
    - 이걸 restAPI에서 동기식으로 모두 처리한다면? 수행속도가 길어지기도 하고, 쿠폰 발급에 실패했는데 가입 자체도 같이 실패하게 되는 등 장애 전파가 발생할 수 있다.
    - 메시지큐를 사용하면 : 메시지를 enqueue하고 응답을 기다리지 않고 다른 동작을 수행할 수 있어서 ‘메시지 전송’이나 ‘쿠폰 발급’에 얼마나 시간이 걸리든 영향을 받지 않을 수 있다. consumer 서버에 장애가 발생하더라도 producer쪽 서버에 영향이 없다. 전달하려는 메시지도 큐에 남아있으므로 consumer 서버가 복구되고나서 재전송할 수 있다.
- 특정한 시간에만 트래픽이 몰리는 경우 (서비스 특성 or 선착순 이벤트 등등)
    - 많은 트래픽을 발생시키는 부분을 메시지 큐에 넣으면 버퍼역할을 하게 된다.
    - consumer를 더 추가할 수 있는 구조라면 message queue를 scale out 하고 consumer를 추가해서 처리량을 늘릴 수 있다.
- 사용할 수 있는 자원에 비해 처리해야할 데이터 양이 엄청 많을 때
- 다수의 어플리케이션이 어떤 데이터 저장소를 공유해야할 때

## 다양한 구현체들의 특징

### **Rabbit MQ**

- AMQP(Advanced Message Queue Protocol)라는 프로토콜의 구현.
- AMQP는 exchange라는 라우터 역할을 하는 컴포넌트가 있다. 여러개의 consumer와 queue가 존재할 때 효율성이 높다.
    
    ![/Untitled1.png](Untitled1.png)
    
    ([https://www.wallarm.com/what/what-is-amqp](https://www.wallarm.com/what/what-is-amqp))
    
- AMQP의 4가지 exchange type
    - Direct Exchange: 메시지는 consumer들 사이에서 로드밸런싱 됨. 유니캐스트에 이상적
    - Fanout Exchange: 바인딩된 모든 큐에 메시지를 라우팅. 메시지를 브로드캐스트 할 때 이상적
    - Topic Exchange: routing key 기반으로 전달
    - Headers Exchange : routing key 대신 메시지 헤더에 다양한 속성을 추가해서 메시지를 전달
- 클러스터링을 지원.

### **Amazon SQS(Simple Queue Service)**

- 메시지를 pull 방식으로 처리한다. fan-out, 메시지 라우팅 등은 지원하지 않는 simple queue.
- 메시지 크기 256KB 제한됨. s3, dynamoDB와 연동하여 더 큰 메시지를 저장할수는 있음.
- 방식
    - standard: 무제한 처리량. At-least-once 메시지 전달(정확히 한번은 아닐 수도 있음), best-effort-ordering(때때로 보낸 순서와 다른 순서로 전달됨)
    - FIFO: TPS제한이 있음. 메시지 전달이 exactly once로 보장되고, 메시지 순서도 보장됨.
- 메시지를 여러 서버에 충분히 중복하여 저장해서 안정성을 보장. 메시지 전달 이후에도 일정 시간 뒤 중복해서 받을 수 있음.
- 강력한 보안, ACL 지원(특정 AWS계정에 대한 메시지의 액세스 권한 제어)
- DLQ(Dead Letter Queue)
    - SQS queue를 생성할 때 DLQ설정을 해두면 producer나 consumer에서 에러가 발생해서 올바르게 처리되지 못한 메시지를 별도의 DLQ에 저장할 수 있다.

### Amazon SNS(Simple Notification Service)

- 사용자에게 푸시/이메일 등을 보낼 때(Application to Person/A2P), 애플리케이션 간의 메시징(Application to Application/A2A) 을 지원한다.
- Fanout 방식.
- A2A의 구독자는 SQS, lambda함수, HTTP/S 엔드포인트 등이 될 수 있다.
    - SQS가 구독자인 형태는 좀 신기했다. 처음엔 queue에서 또다른 queue로 전송해야할 일이 뭐가 있을까 라고 생각하게 되었는데
    - SNS에서 fanout방식으로 여러개의 lambda함수, SQS 등 에 뿌린 다음에 비동기적으로 각각의 역할을 수행하게 하는 구조에선 SQS를 쓸 수 있을 것 같다.
    - [https://seohyun0120.tistory.com/entry/AWS-SNS-vs-SQS-차이점](https://seohyun0120.tistory.com/entry/AWS-SNS-vs-SQS-%EC%B0%A8%EC%9D%B4%EC%A0%90) << 여기서 예시를 보면서 이해할 수 있었다.

### **Apache kafka**

- pub-sub 모델의 분산 메시지 큐
- 대량의 메시지 처리 && 실시간 데이터 처리
- 설정한 보관주기만큼 디스크에 메시지를 저장한다. → 에러 발생 시 다시 consumer에 메시지 전달이 가능
- 확장성이 높다.
- consumer가 메시지를 소비하는 순서가 중요할 때는 적합하지 않다.
- 단순한 TCP기반 프로토콜 사용으로 오버헤드 감소

이외에도 Kinesis, ActiveMQ, Google cloud pub/sub 등등 엄청 다양한데 다 보기엔 어려울 것 같다.

### 언제 어떤 구현체를 쓰면 좋을까?

- 지속성 - 성능 tradeoff
    - 메시지큐 노드가 죽거나 일시적으로 오프라인이 될 수 있다.
    - db처럼 지속성을 갖추려면 디스크에 기록 또는 복제본 생성을 해야하는데, 비용이 든다.
    - 메시지를 잃어도 괜찮다면 메모리에만 메시지를 보관하면서 처리량을 높이고 지연시간을 줄일 수 있다. → RocketMQ, RabbitMQ (RAM node type설정), ActiveMQ
    - 지속성이 더 중요하다면 → Kafka, RabbitMQ(디폴트 설정), SQS
        - (그러나 disk로 전달되기 전에 서버가 죽어서 저장이 안되는 경우까지 보장해주지는 못한다고 한다.)

## References

- 개념
    - [https://shortstories.gitbooks.io/studybook/content/message_queue_c815_b9ac.html](https://shortstories.gitbooks.io/studybook/content/message_queue_c815_b9ac.html)
    - 책 ‘가상면접 사례로 배우는 대규모 시스템 설계 기초’ 1장
    - 책 ‘데이터중심 애플리케이션 설계’ 11장
- 활용 사례
    - 리디북스 kafka [https://ridicorp.com/story/how-to-use-kafka-in-ridi/](https://ridicorp.com/story/how-to-use-kafka-in-ridi/)
    - 여기어때 redis&kafka [https://techblog.gccompany.co.kr/redis-kafka를-활용한-선착순-쿠폰-이벤트-개발기-feat-네고왕-ec6682e39731](https://techblog.gccompany.co.kr/redis-kafka%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%9C-%EC%84%A0%EC%B0%A9%EC%88%9C-%EC%BF%A0%ED%8F%B0-%EC%9D%B4%EB%B2%A4%ED%8A%B8-%EA%B0%9C%EB%B0%9C%EA%B8%B0-feat-%EB%84%A4%EA%B3%A0%EC%99%95-ec6682e39731)
- 구현체
    - 서버리스 패턴 [https://changhoi.kim/posts/serverless/serverless-architecture-pattern/](https://changhoi.kim/posts/serverless/serverless-architecture-pattern/)
    - AWS 메시징 서비스 [https://jaemunbro.medium.com/aws-메시징서비스-비교-kinesis-sqs-sns-ab397a07cb1d](https://jaemunbro.medium.com/aws-%EB%A9%94%EC%8B%9C%EC%A7%95%EC%84%9C%EB%B9%84%EC%8A%A4-%EB%B9%84%EA%B5%90-kinesis-sqs-sns-ab397a07cb1d)
    - SQS [https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
    - SNS [https://docs.aws.amazon.com/ko_kr/sns/latest/dg/welcome-features.html](https://docs.aws.amazon.com/ko_kr/sns/latest/dg/welcome-features.html)
    - SNS와 SQS [https://seohyun0120.tistory.com/entry/AWS-SNS-vs-SQS-차이점](https://seohyun0120.tistory.com/entry/AWS-SNS-vs-SQS-%EC%B0%A8%EC%9D%B4%EC%A0%90)
