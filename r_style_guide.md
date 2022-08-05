# Style guide for R

R is a commonly used language for statistical analysis and data visualisation, however unlike Python, conventions around styling are varied. At CPG, we follow the [Tidyverse Style Guide](https://style.tidyverse.org/); the full overview of syntax can be viewed [here](https://style.tidyverse.org/syntax.html). As laid out in the documentation,  [snake_case](https://en.wikipedia.org/wiki/Snake_case) is used for variable and file naming, with short variable names preferred over long ones (try keeping them to a maximum of two words). Additionally, each R script should be documented with a single or multi-line comment at the start of the script, explaining what the script does and how to use it.

## Code editors and environments
For those that use RStudio, [Styler](https://www.tidyverse.org/blog/2017/12/styler-1.0.0/) can be used as a source code formatter to ensure proper styling. Otherwise, [lintr](https://github.com/r-lib/lintr) can be used to confirm the style guide is adhered to and flag any inconsistencies. 

For those that use VSCode, formatting can be automatically performed by downloading a few extra extensions: the  [languageserver](https://github.com/REditorSupport/languageserver) and the  [R extension](https://marketplace.visualstudio.com/items?itemName=REditorSupport.r) .  Two other helpful  VSCode extensions for debugging include [Error Lens](https://marketplace.visualstudio.com/items?itemName=usernamehw.errorlens) (for enhanced highlighting of errors) and [R Debugger](https://marketplace.visualstudio.com/items?itemName=RDebugger.r-debugger). While the default linter for R within VSCode is R Styler (the tidyverse style guide), the linter can be configured to follow different styles, or avoid specific rules. To generate a minimal lintr file, run `use_lintr()` within an R session (and within the project directory), then edit as per the guidelines [here](https://cran.r-project.org/web/packages/lintr/vignettes/lintr.html). As an example, increasing the line length to 120 characters (instead of 80) would look like this:
```
linters: linters_with_defaults(
    line_length_linter(120), 
  )
```


## Nitpicks:
Some things are not caught by R’s linter, but contribute to more readable code. One of these includes breaking long pieces of code into readable chunks using `-` e.g., 

```
# Load data —————————————

# Plot data —————————————
```

Ensure that breaks extend to the end of the line (80 characters), or follow a consistent length throughout the script. 
