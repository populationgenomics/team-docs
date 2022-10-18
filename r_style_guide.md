# Style guide for R

R is a commonly used language for statistical analysis and data visualisation, however unlike Python, conventions around styling are varied. At CPG, we follow the [Tidyverse Style Guide](https://style.tidyverse.org/); the full overview of syntax can be viewed [here](https://style.tidyverse.org/syntax.html). As laid out in the documentation,  [snake_case](https://en.wikipedia.org/wiki/Snake_case) is used for variable and file naming, with short variable names preferred over long ones (try keeping them to a maximum of two words). Additionally, each R script should be documented with a single or multi-line comment at the start of the script, explaining what the script does and how to use it.

## Code editors and environments

[Styler](https://www.tidyverse.org/blog/2017/12/styler-1.0.0/) is the default source code formatter for R at CPG. To run from any set-up, simply install the styler package by running `install.packages("styler")` in an R session, then run `style_file("my_file_to_style.R")`.

For those that use VSCode, formatting can be automatically performed by downloading a few extra extensions: the  [languageserver](https://github.com/REditorSupport/languageserver) and the  [R extension](https://marketplace.visualstudio.com/items?itemName=REditorSupport.r) .  Two other helpful  VSCode extensions for debugging include [Error Lens](https://marketplace.visualstudio.com/items?itemName=usernamehw.errorlens) (for enhanced highlighting of errors) and [R Debugger](https://marketplace.visualstudio.com/items?itemName=RDebugger.r-debugger).

While the default linter for R within VSCode is R Styler (the tidyverse style guide), some minor differences between the VScode linters and Styler exist (e.g., how open brackets are handled over multiple lines). It is therefore necessary to also run Styler before a script is submitted for review to ensure consistent styling.


## Nitpicks

Some things are not caught by R’s linter, but contribute to more readable code. One of these includes breaking long pieces of code into readable chunks using `-` e.g.,

```r
# Load data —————————————

# Plot data —————————————
```

Ensure that breaks extend to the end of the line (80 characters), or follow a consistent length throughout the script.
