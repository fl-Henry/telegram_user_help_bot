#!/bin/bash

# Exit with waiting for type <enter> before exit
err_exit(){
  echo '[ERROR]'
  printf "%s " "Press enter to continue"
  read -r
  exit "$1"
}

# Get the option
r_key=false
str_param=""

printf "%s " "Params: "
while [ "$#" -gt 0 ]
do
   case "$1" in

  # STDOUT pip freeze
   -f|--freeze)
      r_key=true
      printf "%s " " freeze;"
      ;;

     -h|--help)
      help="--help"
      str_param+="$help "
      printf "%s " " $help';"
      ;;

   -*)
      echo "Invalid option '$1'. Use -h or --help to see the valid options" >&2
      err_exit 1
      ;;

   *)
      echo "Invalid option '$1'. Use -h or --help to see the valid options" >&2
      err_exit 1
   ;;
   esac
   shift
done
echo

# STDOUT present working directory
echo "start_dir: $(pwd)"
start_dir=$(pwd)

# Changing directory to project root directory
echo "base_dir: $(dirname "$0")"
base_dir=$(dirname "$0")
if [ "$base_dir" != "." ]; then
  echo "Changing directory to: $base_dir"
  cd "$base_dir" || err_exit $?
  echo "pwd: $(pwd)"
fi

# Activating virtual environment
echo "Venv activating:"
source ./venv/bin/activate || err_exit $?
echo "Venv activated successful"

# pip freeze if -f or --freeze
if [ "$r_key" = true ]; then
    echo "pip freeze:"
    pip freeze
fi

# Change directory to ./app
echo "cd ./app"
cd ./app || err_exit $?

# Set webhook url
echo "Set Webhook"
python webhook_set.py

# Start flask server
echo "flask run"
flask run -p 8443

# Delete all webhooks
echo "Delete Webhook"
python webhook_delete.py

# Changing directory to initial directory
echo "Changing directory to: $start_dir"
cd "$start_dir" || err_exit $?
echo "pwd: $(pwd)"

# Deactivating virtual environment
deactivate