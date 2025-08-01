import pandas as pd
import os
import logging
import uuid
from datetime import datetime
from .template import TEMPLATE_MAP_OBO, TEMPLATE_MAP_SNOMED

logging.basicConfig(level=logging.INFO)

class Toolkit:
    keywords_OBO = {
        "Birthdate", "Birthyear", "Deathdate", "Sex","Country","Cause-death","Status", "First_visit",
        "Questionnaire", "Diagnosis", "Phenotype", "Symptoms_onset", "Examination", "Laboratory",
        "Genetic", "Disability", "Medication", "Surgery","Hospitalization", "Biobank", "Clinical_trial"
    }

    keywords_SNOMED = {
        "Birthdate", "Birthyear", "Deathdate", "Sex", "Status", "First_visit",
        "Questionnaire", "Diagnosis", "Phenotype", "Symptoms_onset", "Corporal", "Laboratory",
        "Imaging", "Genetic", "Disability", "Medication", "Surgery", "Clinical_trial"
    }

    columns = [
        "model", "pid", "event_id", "value", "age", "value_datatype", "valueIRI", "activity",
        "unit", "input", "target", "protocol_id", "frequency_type", "frequency_value",
        "agent", "startdate", "enddate", "comments"
    ]

    drop_columns = ["value", "valueIRI", "target", "agent", "input", "activity", "unit"]

    @staticmethod
    def milisec():
        now = datetime.now().strftime('%Y%m%d%H%M%S%f')
        return now

    def get_template(self, template_type):
        if template_type == "OBO":
            return TEMPLATE_MAP_OBO
        elif template_type == "SNOMED":
            return TEMPLATE_MAP_SNOMED
        else:
            raise ValueError(f"Template type '{template_type}' not recognized.")

    def whole_method(self, folder_path, template_type):
        matching_files = self._find_matching_files(folder_path, template_type)
        processed = [self._process_file(file, template_type) for file in matching_files]
        final_df = pd.concat(processed, ignore_index=True) if processed else pd.DataFrame(columns=self.columns)
        final_df = self.delete_extra_columns(final_df)
        final_df.to_csv(os.path.join(folder_path, "CARE.csv"), index=False)

    def _find_matching_files(self, folder_path, template_type):
        keywords = self.keywords_OBO if template_type == "OBO" else self.keywords_SNOMED
        return [
            os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if file.endswith(".csv") and any(keyword in file for keyword in keywords)
        ]

    def _process_file(self, filepath, template_type):
        df = self.import_your_data_from_csv(filepath)
        if df is None:
            return pd.DataFrame(columns=self.columns)

        df = self.check_status_column_names(df)
        df = self.add_columns_from_template(df, filepath, template_type)
        df = self.value_edition(df)
        df = self.time_edition(df)
        df = self.clean_empty_rows(df, filepath)
        df = self.unique_id_generation(df)
        return df

    def import_your_data_from_csv(self, filepath):
        try:
            df = pd.read_csv(filepath)
            logging.info(f"Imported CSV: {os.path.basename(filepath)}")
            return df
        except Exception as e:
            logging.error(f"Error loading CSV {filepath}: {e}")
            return None

    def check_status_column_names(self, df):
        extra_cols = set(df.columns) - set(self.columns)
        if extra_cols:
            raise ValueError(f"Unexpected columns: {extra_cols}. Expected: {self.columns}")
        for col in self.columns:
            if col not in df.columns:
                df[col] = pd.Series(dtype=object)
        return df

    def add_columns_from_template(self, df, filepath, template_type):
        template = self.get_template(template_type)
        enriched_rows = []

        for _, row in df.iterrows():
            model = row['model']
            base = {"model": model}
            base.update(template.get(model, {}))
            base.update({k: v for k, v in row.items() if pd.notnull(v)})
            enriched_rows.append(base)

        result = pd.DataFrame(enriched_rows)
        logging.info(f"Transformed: {os.path.basename(filepath)}")
        return result

    def value_edition(self, df):
        def apply_value_types(row):
            model = row.get('model')
            val = row.get('value')
            dtype = row.get('value_datatype')

            if pd.notnull(val):
                if dtype == 'xsd:string' and model != 'Genetic':
                    row['value_string'] = val
                elif dtype == 'xsd:float' and model not in ['Medication', 'Genetic']:
                    row['value_float'] = val
                elif dtype == 'xsd:integer' and model not in ['Medication', 'Genetic']:
                    row['value_integer'] = val
                elif dtype == 'xsd:date':
                    row['value_date'] = val
                elif model == 'Medication':
                    row['concentration_value'] = val
                elif model == 'Genetic':
                    row['output_id_value'] = val

            if 'valueIRI' in row and pd.notnull(row['valueIRI']):
                if model in ['Sex', 'Status', 'Diagnosis', 'Phenotype', 'Clinical_trial', 'Examination', 'Country','Cause-death']:
                    row['attribute_type'] = row['valueIRI']
                elif model in ['Imaging', 'Genetic']:
                    row['output_id'] = row['valueIRI']

            if 'target' in row and pd.notnull(row['target']):
                if model in self.keywords_OBO and model != 'Genetic':
                    row['target_type'] = row['target']
                elif model == 'Genetic':
                    row['attribute_type'] = row['target']

            if 'input' in row and pd.notnull(row['input']):
                if model in self.keywords_OBO:
                    row['input_type'] = row['input']

            if 'agent' in row and pd.notnull(row['agent']):
                if model in ['Biobank', 'Clinical_trial']:
                    row['organization_id'] = row['agent']
                elif model == 'Medication':
                    row['substance_id'] = row['agent']
                elif model == 'Genetic':
                    row['output_type'] = row['agent']

            if 'activity' in row and pd.notnull(row['activity']):
                if model in self.keywords_OBO:
                    row['specific_method_type'] = row['activity']

            if 'unit' in row and pd.notnull(row['unit']):
                if model in ['Examination', 'Laboratory', 'Questionnaire', 'Disability']:
                    row['unit_type'] = row['unit']
                elif model == 'Medication':
                    row['concentration_unit_type'] = row['unit']

            return row

        return df.apply(apply_value_types, axis=1)

    def time_edition(self, df):
        df['enddate'] = df['enddate'].where(pd.notnull(df['enddate']), df['startdate'])
        return df

    def clean_empty_rows(self, df, filepath):
        required_cols = [col for col in ['value', 'valueIRI', 'activity', 'target', 'agent'] if col in df.columns]
        pre_clean_len = len(df)
        df = df[~df[required_cols].isnull().all(axis=1)]
        removed = pre_clean_len - len(df)
        logging.info(f"{os.path.basename(filepath)}: Removed {removed} empty rows")
        return df

    def delete_extra_columns(self, df):
        return df.drop(columns=[col for col in self.drop_columns if col in df.columns], errors='ignore')

    def unique_id_generation(self, df):
        timestamp = self.milisec()
        df['uniqid'] = [f"{timestamp}_{i}" for i in range(len(df))]
        return df