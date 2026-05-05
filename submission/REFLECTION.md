# Reflection — Lab 19

**Tên:** TRỊNH ĐẮC PHÚ
**Cohort:** TDP
**Path đã chạy:** _lite_

---

## Câu hỏi (≤ 200 chữ)

> Trên golden set 50 queries, mode nào thắng ở loại query nào (`exact` /
> `paraphrase` / `mixed`), và tại sao? Khi nào bạn **không** dùng hybrid
> (i.e. khi nào pure BM25 hoặc pure vector là lựa chọn đúng)?

Trên golden set, hybrid thắng trung bình vì nó kết hợp được exact lexical
signal từ BM25 và semantic signal từ vector search. Với `exact` queries, BM25
mạnh nhất hoặc ngang hybrid vì query chứa đúng thuật ngữ trong corpus. Với
`paraphrase`, vector search đáng lẽ có lợi thế, nhưng model lite
`BAAI/bge-small-en-v1.5` không tối ưu cho paraphrase tiếng Việt nên kết quả
không vượt trội. Với `mixed`, hybrid thắng rõ nhất vì query vừa có từ khóa
exact vừa có ý paraphrase, nên RRF tận dụng được cả hai ranked lists.

Tôi sẽ không dùng hybrid khi latency/cost rất chặt, khi keyword matching đã
đủ chính xác cho exact lookup, hoặc khi semantic-only đã đủ tốt cho một domain
ít cần keyword constraints.

---

## Điều ngạc nhiên nhất khi làm lab này

Hybrid không tự động tốt hơn trong mọi slice; chất lượng embedding model và
ngôn ngữ dữ liệu ảnh hưởng mạnh đến phần semantic.

---

## Bonus challenge

- [x] Đã làm bonus (xem `bonus/`)
- [ ] Pair work với: _<tên đồng đội nếu có>_
