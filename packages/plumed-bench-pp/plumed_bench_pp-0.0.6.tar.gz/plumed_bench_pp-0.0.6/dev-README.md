## Hooks:
 - pre-commit
```bash:
#!/bin/bash

#set up the environment here

set -eo pipefail

hatch fmt --formatter --check
echo "Formatter passed"

hatch fmt --linter --check
echo "Linter passed"
```