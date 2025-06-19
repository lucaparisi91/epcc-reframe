.libPaths("packages")

install.packages("plyr",NCores=8,repos="https://www.stats.bris.ac.uk/R")
library("plyr")

# declaring first data frame
data_frame1 <- data.frame(col1 = c(2,4,6), 
                          col2 = c(4,6,8), 
                          col3 = c(8,10,12), 
                          col4 = LETTERS[1:3])
print ("First Dataframe")
print (data_frame1)

# declaring second data frame
data_frame2 <- data.frame(col4 = letters[1:4], 
                          col5 = TRUE)
print ("Second Dataframe")
print (data_frame2)

print ("Combining Dataframe")

# binding data frames
rbind.fill(data_frame1,data_frame2)

print("Success")