#!/bin/bash

# Internal flags for step control
RUN_STEP1=true  # Generate law list
RUN_STEP2=true  # Export law list
RUN_STEP2_1=true # Generate and import summaries
RUN_STEP2_2=true # Generate and import keywords
RUN_STEP3=true  # Generate meta list
RUN_STEP4=true  # Import meta list
RUN_STEP5=true  # Send Discord notification

# Database connection string (e.g., "postgresql://user:password@host:port/database")
# export DATABASE_URL="postgresql://"

# Get current timestamp for unique filenames
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# Define file paths with timestamps
LAW_LIST_FILE="tmp/law_list_${TIMESTAMP}.txt"
LOG_FILE="run_${TIMESTAMP}.log"

# Ensure tmp directory exists
mkdir -p tmp

# Get the number of laws to process from the first argument, default to 50 if not provided
NUM_LAWS=10

# --- Step 1: Generating law list ---
if [ "$RUN_STEP1" = true ]; then
    if [ "$RUN_STEP3" = true ]; then
        SQL="SELECT
            l.xml_law_name
        FROM
            laws l
        WHERE
            l.law_metadata IS NULL
        ORDER BY
            (
                SELECT COUNT(*)
                FROM law_relationships lr
                WHERE lr.main_law_id = l.id OR lr.related_law_id = l.id
            ) DESC,
            CASE l.xml_law_nature
                WHEN '憲法' THEN 3
                WHEN '法律' THEN 2
                WHEN '命令' THEN 1
                ELSE 0
            END DESC,
            l.xml_latest_change_date DESC limit ${NUM_LAWS};"
    else
	    SQL="SELECT xml_law_name from laws where (llm_summary IS NULL or llm_keywords IS NULL) and (law_metadata is not NULL) ORDER BY xml_law_name limit ${NUM_LAWS};"
    fi
    echo "$SQL"
    psql "${DATABASE_URL}" -c "${SQL}" | sed '1,2d; $d' | sed '$d' > "${LAW_LIST_FILE}"

    if [ ! -s "$LAW_LIST_FILE" ]; then 
        echo i"$LAW_LIST_FILE size 0. Exiting."
        exit 1
    fi
fi

# --- Step 2: Exporting law list ---
if [ "$RUN_STEP2" = true ]; then
    echo "--- Step 2: Exporting law list from ${LAW_LIST_FILE} ---"
    python law_cli.py --export-law-list "${LAW_LIST_FILE}" --output-dir output

    if [ $? -ne 0 ]; then
        echo "Error: Step 2 failed. Exiting."
        exit 1
    fi
fi

# --- Step 2.1: Generating summary files and importing them ---
if [ "$RUN_STEP2_1" = true ]; then
    echo "--- Step 2.1: Generating summary files and importing them ---"
    python law_cli.py --generate-summary-from-md --law-list "${LAW_LIST_FILE}" --summary-example-file output/summary_sample.md --output-dir output
    if [ $? -ne 0 ]; then
        echo "Error: Step 2.1 (Generate Summary) failed. Exiting."
        exit 1
    fi
    python law_cli.py --update-summary output/all_laws_summary.md --law-list "${LAW_LIST_FILE}"
    if [ $? -ne 0 ]; then
        echo "Error: Step 2.1 (Import Summary) failed. Exiting."
        exit 1
    fi
fi

# --- Step 2.2: Generating keyword files and importing them ---
if [ "$RUN_STEP2_2" = true ]; then
    echo "--- Step 2.2: Generating keyword files and importing them ---"
    python law_cli.py --generate-keywords-from-md --law-list "${LAW_LIST_FILE}" --output-file output/keywords_sample.csv
    if [ $? -ne 0 ]; then
        echo "Error: Step 2.2 (Generate Keywords) failed. Exiting."
        exit 1
    fi
    python law_cli.py --update-keywords output/keywords_sample.csv --law-list "${LAW_LIST_FILE}"
    if [ $? -ne 0 ]; then
        echo "Error: Step 2.2 (Import Keywords) failed. Exiting."
        exit 1
    fi
fi

# --- Step 3: Generating meta list ---
if [ "$RUN_STEP3" = true ]; then
    echo "--- Step 3: Generating meta list and logging to ${LOG_FILE} ---"
    python law_cli.py --generate-meta-list --law-list "${LAW_LIST_FILE}" | tee "${LOG_FILE}"

    if [ $? -ne 0 ]; then
        echo "Error: Step 3 failed. Exiting."
        exit 1
    fi
fi

# --- Step 4: Importing meta list ---
if [ "$RUN_STEP4" = true ]; then
    echo "--- Step 4: Importing meta list from ${LAW_LIST_FILE} ---"
    python law_cli.py --import-meta-list --law-list "${LAW_LIST_FILE}"

    if [ $? -ne 0 ]; then
        echo "Error: Step 4 failed. Exiting."
        exit 1
    fi
fi

# --- Step 5: Sending Discord notification ---
if [ "$RUN_STEP5" = true ]; then
    echo "--- Step 5: Sending Discord notification ---"
    curl -X POST -H 'Content-type: application/json' --data "{\"content\": \"灌 ${NUM_LAWS} 筆資料完成\"}" ${DISCORD_URL} 

    if [ $? -ne 0 ]; then
        echo "Warning: Discord notification failed."
    fi
fi

echo "--- Automation script finished ---"
