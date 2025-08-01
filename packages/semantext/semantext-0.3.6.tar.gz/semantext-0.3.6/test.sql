WITH "f52cd533-2786-40bc-b724-94cf440a3a16" AS (
  SELECT DISTINCT
    "datalake"."remix"."dim_snif"."snif_id" AS "snif_id",
    "datalake"."remix"."dim_snif"."snif_name" AS "snif_name",
    "datalake"."remix"."dim_snif"."ir" AS "ir"
  FROM "datalake"."remix"."dim_snif"
  WHERE
    "datalake"."remix"."dim_snif"."ir" = CAST('Jerusalem' AS VARCHAR)
), "3045d8cb-58fb-4ab0-9f8b-fcc59c0f4329" AS (
  SELECT
    AVG("datalake"."remix"."sales_fact"."amount") AS "sales_fact_amount",
    SUM("datalake"."remix"."sales_fact"."price") AS "sales_fact_price",
    "f52cd533-2786-40bc-b724-94cf440a3a16"."snif_id" AS "snif_id"
  FROM "datalake"."remix"."sales_fact"
  INNER JOIN "f52cd533-2786-40bc-b724-94cf440a3a16"
    ON "f52cd533-2786-40bc-b724-94cf440a3a16"."snif_id" = "datalake"."remix"."sales_fact"."snif_id"
  WHERE
    "datalake"."remix"."sales_fact"."taarich" = CAST('2023-01-01' AS TIMESTAMP)
  GROUP BY
    "f52cd533-2786-40bc-b724-94cf440a3a16"."snif_id"
), "d871d67f-8858-4d71-afcd-90864a2d403d" AS (
  SELECT
    AVG("datalake"."remix"."shalom_fact"."amount") AS "shalom_fact_amount",
    "f52cd533-2786-40bc-b724-94cf440a3a16"."ir" AS "ir"
  FROM "datalake"."remix"."shalom_fact"
  INNER JOIN "f52cd533-2786-40bc-b724-94cf440a3a16"
    ON "f52cd533-2786-40bc-b724-94cf440a3a16"."ir" = "datalake"."remix"."shalom_fact"."ir"
  GROUP BY
    "f52cd533-2786-40bc-b724-94cf440a3a16"."ir"
)
SELECT
  "f52cd533-2786-40bc-b724-94cf440a3a16"."snif_id" AS "snif_id",
  "f52cd533-2786-40bc-b724-94cf440a3a16"."snif_name" AS "snif_name",
  "3045d8cb-58fb-4ab0-9f8b-fcc59c0f4329"."sales_fact_amount",
  "3045d8cb-58fb-4ab0-9f8b-fcc59c0f4329"."sales_fact_price",
  "d871d67f-8858-4d71-afcd-90864a2d403d"."shalom_fact_amount"
FROM "f52cd533-2786-40bc-b724-94cf440a3a16"
LEFT JOIN "3045d8cb-58fb-4ab0-9f8b-fcc59c0f4329"
  ON "3045d8cb-58fb-4ab0-9f8b-fcc59c0f4329"."snif_id" = "f52cd533-2786-40bc-b724-94cf440a3a16"."snif_id"
LEFT JOIN "d871d67f-8858-4d71-afcd-90864a2d403d"
  ON "d871d67f-8858-4d71-afcd-90864a2d403d"."ir" = "f52cd533-2786-40bc-b724-94cf440a3a16"."ir"