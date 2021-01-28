library(ggplot2)
library(dplyr)
library(stringr)
library(tidyr)

data <- read.csv('asunnot.csv') %>%
  mutate(
    street = paste0(city, ", ", word(address, 1))
  )

data$street[grepl("Valkeakoski", data$street)] = "Valkeakoski"

means <- data %>%
  group_by(street) %>%
  summarize(mean = mean(price_per_area)) %>% as.data.frame() %>%
  mutate(min = min(data$size),
         max = max(data$size)) %>%
  pivot_longer(cols = c("min", "max"))


ggplot() + geom_jitter(data = data, aes(x = size, y = price_per_area, color = street), width = 2) + 
geom_smooth(data = data, aes(x = size, y = price_per_area, color = street), method = "gam", 
            formula = y ~ s(x, k = 3)) +
  geom_line(data = means, aes(x = value, y = mean, color = street))
