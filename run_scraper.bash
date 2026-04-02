#!/bin/bash

# Активируем виртуальное окружение, если оно есть
if [ -d ".venv" ]; then
    echo "Активация виртуального окружения..."
    source .venv/bin/activate
    pip3 install -r requirements.txt
fi

# Параметры: начальная страница, конечная страница, выходной файл
START_PAGE=${1:-1}
END_PAGE=${2:-10}
CATEGORY_ID=${3:-3}
OUTPUT_FILE=${4:-out.csv}

echo "Обработка страниц с $START_PAGE по $END_PAGE"
echo "Результаты будут сохранены в $OUTPUT_FILE"

for ((page=$START_PAGE; page<=$END_PAGE; page++)); do
    echo "Обработка страницы $page..."
    python3 parse.py $page $CATEGORY_ID $OUTPUT_FILE
    
    if [ $? -ne 0 ]; then
        echo "ОШИБКА при обработке страницы $page"
        exit 1
    fi
    
    if [ $page -lt $END_PAGE ]; then
        echo "Ожидание 6 секунд перед следующей страницей..."
        sleep 6
    fi
done

echo "Все страницы обработаны. Результаты в $OUTPUT_FILE"
