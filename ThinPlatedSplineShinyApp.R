library(shiny)
library(MASS)
library(rgl)
library(RColorBrewer)
library(lattice)
library(dplyr)
library(fields)
library(plotly)

set.seed(12345)
scale_noise = 0.5
g <- expand.grid(x=seq(-1,1,length.out = 10),
                 y=seq(-1,1,length.out = 10))

g$z <- g$x^2 - g$y^2
grows <- nrow(g)
g$noise <- scale_noise*rnorm(grows)
g$TARGET <- g$z + g$noise
x <- matrix(g$x,nrow=sqrt(grows),ncol=sqrt(grows))
y <- matrix(g$y,nrow=sqrt(grows),ncol=sqrt(grows))
z <- matrix(g$z,nrow=sqrt(grows),ncol=sqrt(grows))
noise <- matrix(g$noise,nrow=sqrt(grows),ncol=sqrt(grows))
TARGET <- matrix(g$TARGET,nrow=sqrt(grows),ncol=sqrt(grows))


server <- function(input, output) {
  output$plotlyPlot <- renderPlotly({
    input$actionButton
    if(isolate(input$GCVradio)=="GCV"){
      tpsFit <- Tps(x=g[c("x","y")],Y = g$TARGET)
    }else{
      tpsFit <- Tps(x=g[c("x","y")],Y = g$TARGET,
                    lambda=as.numeric(isolate(input$lambda)))}
    print("2")
    g$tpsFit <- tpsFit$fitted.values
    tpsFitM <- matrix(g$tpsFit,nrow=sqrt(grows),ncol=sqrt(grows))
    print(length(tpsFitM))
    p <- plot_ly(x=x,y=y,z=z,type="surface",
                 visible=ifelse(input$radio1=="On",TRUE,FALSE),
                 colorscale="Reds",showscale=FALSE) %>%
      add_trace(x=c(x),y=c(y),z=c(TARGET),
                mode="markers",color="red",type="scatter3d",
                visible=ifelse(input$radio2=="On",TRUE,FALSE)) %>%
      add_trace(x=x,y=y,z=tpsFitM,type="surface",
                visible=ifelse(input$radio3=="On",TRUE,FALSE),
                colorscale = "Blues",showscale=FALSE)
    print("3")
    p
  })
  
  output$lambdaText <- renderText({
    input$actionButton
    if(isolate(input$GCVradio)=="GCV"){
      tpsFit <- Tps(x=g[c("x","y")],Y = g$TARGET)
      lambda <- as.character(tpsFit$lambda)
    }else{lambda <- isolate(input$lambda)}
    lambda  <- paste("Lambda Shown: ",lambda,sep = " ")
  })
}

ui <- fluidPage(
  fluidRow(
    column(3,
           radioButtons("radio1", label = "True Surface",
                        choices = list("On"="On","Off"="Off"),selected="On"),
           radioButtons("radio2", label = "Observed Values",
                        choices = list("On"="On","Off"="Off"),selected="Off"),
           radioButtons("radio3", label = "Thin Plate Spline",
                        choices = list("On"="On","Off"="Off"),selected="Off"),
           textInput("lambda","Lambda",value="0"),
           actionButton("actionButton","Fit"),
           radioButtons("GCVradio","User or GCV Lambda",
                        choices = list("User Selected Lambda"="user",
                                       "GCV Lambda"="GCV")),
           textOutput("lambdaText")
    ),
    column(9,plotlyOutput("plotlyPlot",height = "800px"))
  )
)


shinyApp(ui = ui, server = server)