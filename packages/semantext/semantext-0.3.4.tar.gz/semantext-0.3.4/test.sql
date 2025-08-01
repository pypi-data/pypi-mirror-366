WITH "29326c66-9edf-4d77-9bc4-6f9f7e68b827" AS (
  SELECT DISTINCT
    "datalake"."remix"."dim_snif"."snif_id" AS "snif_id",
    "datalake"."remix"."dim_snif"."snif_name" AS "snif_name",
    "datalake"."remix"."dim_snif"."ir" AS "ir"
  FROM "datalake"."remix"."dim_snif"
  WHERE
    "datalake"."remix"."dim_snif"."ir" = CAST('Jerusalem' AS VARCHAR)
), "f904a235-9a9a-4650-9f42-f58f2994bace" AS (
  SELECT
    AVG("datalake"."remix"."sales_fact"."amount") AS "sales_fact_amount",
    SUM("datalake"."remix"."sales_fact"."price") AS "sales_fact_price",
    "29326c66-9edf-4d77-9bc4-6f9f7e68b827"."snif_id" AS "snif_id"
  FROM "datalake"."remix"."sales_fact"
  INNER JOIN "29326c66-9edf-4d77-9bc4-6f9f7e68b827"
    ON "29326c66-9edf-4d77-9bc4-6f9f7e68b827"."snif_id" = "datalake"."remix"."sales_fact"."snif_id"
  WHERE
    "datalake"."remix"."sales_fact"."taarich" = CAST('2023-01-01' AS TIMESTAMP)
  GROUP BY
    "29326c66-9edf-4d77-9bc4-6f9f7e68b827"."snif_id" AS "snif_id"
), "22eb79a3-719a-44da-80d0-d304befcc3e7" AS (
  SELECT
    AVG("datalake"."remix"."shalom_fact"."amount") AS "shalom_fact_amount",
    "29326c66-9edf-4d77-9bc4-6f9f7e68b827"."ir" AS "ir"
  FROM "datalake"."remix"."shalom_fact"
  INNER JOIN "29326c66-9edf-4d77-9bc4-6f9f7e68b827"
    ON "29326c66-9edf-4d77-9bc4-6f9f7e68b827"."ir" = "datalake"."remix"."shalom_fact"."ir"
  GROUP BY
    "29326c66-9edf-4d77-9bc4-6f9f7e68b827"."ir" AS "ir"
)
SELECT
  "29326c66-9edf-4d77-9bc4-6f9f7e68b827"."snif_id" AS "snif_id",
  "29326c66-9edf-4d77-9bc4-6f9f7e68b827"."snif_name" AS "snif_name",
  "f904a235-9a9a-4650-9f42-f58f2994bace"."sales_fact_amount",
  "f904a235-9a9a-4650-9f42-f58f2994bace"."sales_fact_price",
  "22eb79a3-719a-44da-80d0-d304befcc3e7"."shalom_fact_amount"
FROM "29326c66-9edf-4d77-9bc4-6f9f7e68b827"
LEFT JOIN "f904a235-9a9a-4650-9f42-f58f2994bace"
  ON "f904a235-9a9a-4650-9f42-f58f2994bace"."snif_id" = "29326c66-9edf-4d77-9bc4-6f9f7e68b827"."snif_id"
LEFT JOIN "22eb79a3-719a-44da-80d0-d304befcc3e7"
  ON "22eb79a3-719a-44da-80d0-d304befcc3e7"."ir" = "29326c66-9edf-4d77-9bc4-6f9f7e68b827"."ir"