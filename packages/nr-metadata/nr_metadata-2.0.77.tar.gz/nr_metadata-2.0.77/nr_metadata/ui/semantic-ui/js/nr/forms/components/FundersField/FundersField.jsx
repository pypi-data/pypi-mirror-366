import React from "react";
import PropTypes from "prop-types";
import { ArrayField, TextField } from "react-invenio-forms";
import { i18next } from "@translations/nr/i18next";
import { LocalVocabularySelectField } from "@js/oarepo_vocabularies";
import { ArrayFieldItem, useFieldData } from "@js/oarepo_ui";

export const FundersField = ({ fieldPath, addButtonLabel }) => {
  const { getFieldData } = useFieldData();

  return (
    <ArrayField
      addButtonLabel={addButtonLabel}
      defaultNewValue={{}}
      fieldPath={fieldPath}
      {...getFieldData({ fieldPath, fieldRepresentation: "text" })}
      addButtonClassName="array-field-add-button"
    >
      {({ arrayHelpers, indexPath }) => {
        const fieldPathPrefix = `${fieldPath}.${indexPath}`;
        return (
          <ArrayFieldItem
            indexPath={indexPath}
            arrayHelpers={arrayHelpers}
            style={{ display: "block" }}
            fieldPathPrefix={fieldPathPrefix}
          >
            <TextField
              width={16}
              fieldPath={`${fieldPathPrefix}.projectID`}
              {...getFieldData({
                fieldPath: `${fieldPathPrefix}.projectID`,
                fieldRepresentation: "compact",
              })}
            />
            <TextField
              className="rel-mt-1"
              width={16}
              fieldPath={`${fieldPathPrefix}.projectName`}
              {...getFieldData({
                fieldPath: `${fieldPathPrefix}.projectName`,
                fieldRepresentation: "compact",
              })}
            />
            <TextField
              className="rel-mt-1"
              width={16}
              fieldPath={`${fieldPathPrefix}.fundingProgram`}
              {...getFieldData({
                fieldPath: `${fieldPathPrefix}.fundingProgram`,
                fieldRepresentation: "compact",
              })}
            />
            <LocalVocabularySelectField
              className="rel-mt-1"
              width={16}
              fieldPath={`${fieldPathPrefix}.funder`}
              optionsListName="funders"
              clearable
              {...getFieldData({
                fieldPath: `${fieldPathPrefix}.funder`,
                fieldRepresentation: "compact",
              })}
            />
          </ArrayFieldItem>
        );
      }}
    </ArrayField>
  );
};

FundersField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  addButtonLabel: PropTypes.string,
};

FundersField.defaultProps = {
  addButtonLabel: i18next.t("Add project/financing information"),
};
