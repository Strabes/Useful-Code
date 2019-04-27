## Import everything we'll need
import findspark
findspark.init()
from pyspark import SparkContext, sql
import itertools
from pyspark.sql import functions as F
import pandas as pd
import matplotlib.pyplot as plt

def hist_cat_(spdf,variables):
    """
    Create histogram for variable(s) "variables" of SparkContext
    DataFrame spdf
    
    Inputs:
    spdf: Spark Data Frame
    variables: string or list of name(s) of column(s) to histogram
    
    Output:
    Spark DataFrame with columns: variables, "_COUNT_",
    "_PERCENT_", "_CUM_PERCENT_", "_RANK_"
    """
    if type(variables) is str:
        variables = [variables]
	
    ## Window for all rows
    TotalWindow = sql.Window\
        .rowsBetween(
        sql.Window.unboundedPreceding,
        sql.Window.unboundedFollowing)

    ## Window for unbounded preceding to current row
    CumulativeWindow = sql.Window\
        .rowsBetween(
        sql.Window.unboundedPreceding,
        sql.Window.currentRow)

    ## Construct grouped-summary
    df = spdf.groupBy(variables)\
         .agg(F.count(variables[0]).alias("_COUNT_"))\
         .withColumn("_PERCENT_",
                     F.col('_COUNT_')/F.sum(F.col('_COUNT_'))\
                     .over(TotalWindow))\
         .sort("_COUNT_",ascending = False)\
         .withColumn("_CUM_PERCENT_",F.sum(F.col("_PERCENT_"))\
                     .over(CumulativeWindow))\
         .withColumn("_RANK_",F.row_number()
                     .over(sql.Window().orderBy(F.col("_COUNT_").desc())))
        
    return(df)

def hist_cat_group_(spdf,var,otherlevel = "_OTHER_",
    maxlevels = None, mincumulative = None):
    """
    Create histogram for variable "var" of Spark
    DataFrame spdf using at most "maxlevels" levels or number of levels
	required to achieve "mincumulative" percent of records. All
	other levels are grouped as "otherlevel"
    
    Inputs:
    spdf: Spark Data Frame
    var: string name of column to histogram
    
    Output:
    Spark DataFrame with columns: var, "_COUNT_",
    "_PERCENT_", "_CUM_PERCENT_", "_RANK_"
    """
	
    ## Window for all rows
    TotalWindow = sql.Window \
        .rowsBetween(
        sql.Window.unboundedPreceding,
        sql.Window.unboundedFollowing)

    ## Window for unbounded preceding to current row
    CumulativeWindow = sql.Window \
        .rowsBetween(
        sql.Window.unboundedPreceding,
        sql.Window.currentRow)
    
    df = hist_cat_(spdf,var)
    
    if maxlevels is not None or mincumulative is not None:
        if maxlevels is None:
            maxlevels = df.where("_CUM_PERCENT_ >= " + mincumulative) \
                .first().asDict()["_RANK_"]
                
        ## Substitute other level
        df = (df
            .withColumn(
            var,
            F.when(F.col("_RANK_") > maxlevels, otherlevel)
            .otherwise(F.col(var))
            ).groupBy(var)
         .agg(F.sum("_COUNT_").alias("_COUNT_"))
         .withColumn("_PERCENT_",
                     F.col('_COUNT_')/F.sum(F.col('_COUNT_'))
                     .over(TotalWindow))
         .sort("_COUNT_",ascending = False)
         .withColumn("_CUM_PERCENT_",F.sum(F.col("_PERCENT_"))
                     .over(CumulativeWindow))
         .withColumn("_RANK_",F.row_number()
                     .over(sql.Window().orderBy(F.col("_COUNT_").desc()))
                     )
                     )
    
    return(df)