WITH "00140aa0-3c80-4dad-a3ea-270a82c57d2f" AS (
  SELECT DISTINCT
    "datalake"."remix"."dim_snif"."snif_id" AS "snif_id",
    "datalake"."remix"."dim_snif"."snif_name" AS "snif_name",
    "datalake"."remix"."dim_snif"."ir" AS "ir"
  FROM "datalake"."remix"."dim_snif"
  WHERE
    "datalake"."remix"."dim_snif"."ir" = CAST('Jerusalem' AS VARCHAR)
), "d695e288-49c5-46f8-aa34-6dea89be8785" AS (
  SELECT
    AVG("datalake"."remix"."sales_fact"."amount") AS "sales_fact_amount",
    SUM("datalake"."remix"."sales_fact"."price") AS "sales_fact_price",
    "00140aa0-3c80-4dad-a3ea-270a82c57d2f"."snif_id" AS "snif_id"
  FROM "datalake"."remix"."sales_fact"
  INNER JOIN "00140aa0-3c80-4dad-a3ea-270a82c57d2f"
    ON "00140aa0-3c80-4dad-a3ea-270a82c57d2f"."snif_id" = "datalake"."remix"."sales_fact"."snif_id"
  WHERE
    "datalake"."remix"."sales_fact"."taarich" = CAST('2023-01-01' AS TIMESTAMP)
  GROUP BY
    "00140aa0-3c80-4dad-a3ea-270a82c57d2f"."snif_id" AS "snif_id"
), "0d9624c7-d9ba-4aa7-b8cd-8da75c427829" AS (
  SELECT
    AVG("datalake"."remix"."shalom_fact"."amount") AS "shalom_fact_amount",
    "00140aa0-3c80-4dad-a3ea-270a82c57d2f"."ir" AS "ir"
  FROM "datalake"."remix"."shalom_fact"
  INNER JOIN "00140aa0-3c80-4dad-a3ea-270a82c57d2f"
    ON "00140aa0-3c80-4dad-a3ea-270a82c57d2f"."ir" = "datalake"."remix"."shalom_fact"."ir"
  GROUP BY
    "00140aa0-3c80-4dad-a3ea-270a82c57d2f"."ir" AS "ir"
)
SELECT
  "00140aa0-3c80-4dad-a3ea-270a82c57d2f"."snif_id" AS "snif_id",
  "00140aa0-3c80-4dad-a3ea-270a82c57d2f"."snif_name" AS "snif_name",
  "d695e288-49c5-46f8-aa34-6dea89be8785"."sales_fact_amount",
  "d695e288-49c5-46f8-aa34-6dea89be8785"."sales_fact_price",
  "0d9624c7-d9ba-4aa7-b8cd-8da75c427829"."shalom_fact_amount"
FROM "00140aa0-3c80-4dad-a3ea-270a82c57d2f"
LEFT JOIN "d695e288-49c5-46f8-aa34-6dea89be8785"
  ON "d695e288-49c5-46f8-aa34-6dea89be8785"."snif_id" = "00140aa0-3c80-4dad-a3ea-270a82c57d2f"."snif_id"
LEFT JOIN "0d9624c7-d9ba-4aa7-b8cd-8da75c427829"
  ON "0d9624c7-d9ba-4aa7-b8cd-8da75c427829"."ir" = "00140aa0-3c80-4dad-a3ea-270a82c57d2f"."ir"