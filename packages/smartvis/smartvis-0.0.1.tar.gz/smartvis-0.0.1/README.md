# SmartVis
A PY Library that can visualize Data Frames in a smarter way.

# Installation and About
```
pip install smartvis
```

 This is a wrap around **Plotly** for accessing the relationship between dataframe columns. This package cuts the cost of manual entry to find the realtionship between columns.

 # Parameters in visualizeEverything function
  ```
  visualizeEverything(df, iColumns, maxGraph, maxPermutations, permute)
  ```
* **df**: DataFrame that needs to be passed, which needs to be visualized *(Cleaned DF is preferred)*.
* **iColumns** (Optional): Takes a list of column names which nees to be visualized specifically.
* **maxGraph** (Optional): Takes an Integer, that plots maximum number of graphs, if set to one, will plot 1 graph.
* **maxPermutations** (Optional): Takes an Integer, that plots maximum number of column combinations.
* **permute** (Optional): Takes a bool, returns Permutation or Combination sorting. ([Reference to know more](https://betterexplained.com/articles/easy-permutations-and-combinations/))

 # Example Usage
 **Example Cleaned DataSet**:
 |       | Name    | Age | City          |
|-------|---------|-----|---------------|
| **0** | Alice   | 25  | New York      |
| **1** | Bob     | 30  | San Francisco |
| **2** | Charlie | 22  | Chicago       |


1. After Installing:
   ```
   pip install smartvis
   ```
2. Import the package to the file:
   ```
   from smartvis import visualizeEverything
   ```
   <p align="center"> or </p>

    ```
    from smartvis import visualizeEverything as ve
    ```
3. Code for **Visualizing**
    * Senario 1:  
       ```
       from smartvis import visualizeEverything
       import pandas as pd
       df=pd.read_csv("cleanedDS.csv")
       visualizeEverything(df,maxGraph=2, maxPermutations=2)
       ```
       Plots a **Scatter Plot** of 2 Graphs:
        1. **Name and Age**
        2. **Age and City**
  
  
     * Senario 2:
       ```
       from smartvis import visualizeEverything as ev
       import pandas as pd
       df=pd.read_csv("cleanedDS.csv")
       ve(df,maxGraph=2, maxPermutations=2,premute=True)
       ```
       Plots a **Scatter Plot** of 2 Graphs:
        1. **Name and Age**
        2. **Age and Name**
     
     * Senario 3:
       ```
       from smartvis import visualizeEverything as ev
       import pandas as pd
       df=pd.read_csv("cleanedDS.csv")
       ve(df,maxGraph=1,premute=True)
       ```
       Plots a **Scatter Plot** of 1 Graph:
         1. **Name and Age**
  
    * Senario 4: 
      ```
      from smartvis import visualizeEverything as ev
      import pandas as pd
      df=pd.read_csv("cleanedDS.csv")
      ve(df,iColumns=["Age","City"],maxGraph=2,maxPermutations=1)
      ```
      Plots a **Scatter Plot** of 1 Graph: *(will only plot one graph as premute is false and it won't return more than 1 Graph for one Column)*
        1. **Name and Age**
      
    * Senario 5:
      ```
      from smartvis import visualizeEverything as ev
      import pandas as pd
      df=pd.read_csv("cleanedDS.csv")
      ve(df, maxGraph=1, maxPermutations=3,premute=True)
      ```
      Plots a **Scatter Plot** of 3 Graph:
        1. **Name and Age**
        2. **Age and Name**
        3. **City and Name**
