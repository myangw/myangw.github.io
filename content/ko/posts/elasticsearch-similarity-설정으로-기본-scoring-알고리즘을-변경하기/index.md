---
title: "elasticsearch - similarity 설정으로 기본 scoring 알고리즘을 변경하기"
date: 2021-02-11T00:00:00+09:00
slug: "elasticsearch - similarity 설정으로 기본 scoring 알고리즘을 변경하기"
summary: "디폴트 알고리즘으로 원하는 결과가 안나올 때"
tags:
  - elasticsearch
draft: false
ShowToc: true
TocOpen: false
---

(elasticsearch 7.10 기준으로 작성)

## 어떤 상황에서 similarity를 설정하면 좋을까

elasticsearch는 흔히 로그 분석/관리 시스템이나 full-text search용도로 쓰인다. 하지만 지난번 + 이번에 내가 맡은 프로젝트에서는 full-text search가 필요없는 컨텐츠에 대한 검색엔진 용도로 elasticsearch를 사용했다. 이를테면  `A필드가 매칭되는게 1순위, 없으면 B필드가 매칭되는게 2순위...` 와 같은 여러 개의 조건들을 충족시키는 결과를 찾는 것이다. 내가 작성한 쿼리 조건에 매칭되는지 아닌지가 중요하고 document가 검색 키워드를 몇개나 가지고 있는지 등등은 중요하지 않았다. 그런데 기본 알고리즘이 적용되다보니 tf, idf 등의 점수때문에 완전히 A, B 필드에 대한 score 순으로 정렬되지는 않았다. 이런 상황에서 필요한 것이 similarity(유사도, scoring algorithm) 를 설정하는 것이다.

## 어떻게 변경??

어떤 document를 높은 순위로 결과를 뽑을 것인지에 대해 elasticsearch는 기본적으로 [Okapi BM25 알고리즘](https://en.wikipedia.org/wiki/Okapi_BM25) (과거에는 TF/IDF) 을 사용하여 score를 계산한다. 이 score를 1순위로 해서 정렬한 결과를 리턴하는게 디폴트다. 여기서 쓰이는 알고리즘을 similarity 설정으로 변경할 수 있다. 

[공식 문서](https://www.elastic.co/guide/en/elasticsearch/reference/current/similarity.html)를 보면 별도 설정 없이 선택할 수 있는 디폴트 알고리즘은 3개이다.

- BM25  ← 버전7 기준 디폴트
- classic ← 예전 디폴트인 TF/IDF알고리즘 기반
- **boolean** ← full-text ranking이 필요하지 않을 때 선택할 수 있다. 오직 쿼리 텀이 매치되었는지를 기준으로 scoring한다. score는 쿼리의 boost만큼 부여한다.

디폴트 알고리즘은 키워드가 문서에서 얼마나 자주 나타나는지, 모든 문서에서 자주 등장하는지 특정 문서에서만 자주 등장하는지 등을 계산하여 키워드의 중요도에 따른 검색결과를 뽑아내는데 최적화되어있다. 이런  파라미터들이 완전히 무시되어도 괜찮다면 boolean으로 similarity를 변경하면 된다. 

### Custom similarity 정의하기

커스텀하게 파라미터를 튜닝하거나 스크립트를 짜서  similarity를 정의하고 필요한 필드에 적용해서 사용할 수 수도 있다. 지난 프로젝트 때는 가장 마지막 정렬 순위로 tf를 반영해야하는 요구사항이 있어서 이 방식을 썼다.

- **elasticsearch 제공 similarity**
    - type에 type name이 들어가고 다른 option들은 type에 따라서 알고리즘 공식에 들어가는 parameter의 값들을 넣어줄 수 있다. ([가능한 type과 옵션은 공식문서 참조](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules-similarity.html#_available_similarities))

    ```java
    ## 예시 - DFR similarity일때

    PUT /index
    {
      "settings": {
        "index": {
          "similarity": {
            "my_similarity": {
              "type": "DFR",
              "basic_model": "g",
              "after_effect": "l",
              "normalization": "h2",
              "normalization.h2.c": "3.0"
            }
          }
        }
      }
    }
    ```

    - 위 예시에서 정의한 my_similarity를 indexing할 때 필드 매핑하는 부분에서 넣어주면 해당 필드에만 적용이 된다.

    ```java
    "mappings": {
        "properties": {
          "my_field": {
            "type": "text",
            "similarity": "my_similarity"
          }
        }
      }
    ```

    - 디폴트 알고리즘인 BM25에도 파라미터를 바꿔서 변경을 줄 수 있다.

        ![bm25.png](bm25.png)

        - 공식문서 아래에 보면 스크립트로 이 공식을 표현했다.
            - boost * idf * tf
                - idf : log(1 + (N - n + 0.5) / (n + 0.5))
                - tf: freq / (freq + k1 * (1 - b + b * dl / avgdl)
        - 여기서 k1, b 값을 파라미터로 넣어줄 수 있다.
            - [https://jitwo.tistory.com/8](https://jitwo.tistory.com/8)
            - idf score는 조정하지 못하고 tf만 가능

- **Scripted similarity**
    - 알고리즘 통째로 내가 script를 짤 수도 있다. 잘 모른다면 다소 위험한 방식일 수 있고 지켜야하는 rule도 있다.
    - 그럼에도 idf 영향을 없애고 tf만 남겨두고싶어서 썼다. 기본 bm25 알고리즘을 조금 변형했다.

        ```
        double tf = Math.sqrt(doc.freq); return query.boost * tf
        ```

        - painless라는 스크립트 언어를 쓴다. 😫
        - 접근 가능한 variable들은 [여기에](https://www.elastic.co/guide/en/elasticsearch/painless/current/painless-similarity-context.html) 나와있다.

TODO:  [constant score query](https://www.elastic.co/guide/en/elasticsearch/painless/current/painless-similarity-context.html)를 뒤늦게 발견했는데, boolean similarity 적용하는 것과 비슷해보이는데 좀더 알아봐야 할 듯 하다.

### 참고

[https://www.elastic.co/guide/en/elasticsearch/reference/current/similarity.html](https://www.elastic.co/guide/en/elasticsearch/reference/current/similarity.html) 

[https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules-similarity.html](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules-similarity.html) 

[https://saskia-vola.com/when-simple-is-better-the-boolean-similarity-module](https://saskia-vola.com/when-simple-is-better-the-boolean-similarity-module)