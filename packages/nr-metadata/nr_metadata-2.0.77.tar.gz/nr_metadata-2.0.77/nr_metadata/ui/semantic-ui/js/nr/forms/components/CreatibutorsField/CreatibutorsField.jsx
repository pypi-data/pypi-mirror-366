// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { getIn, FieldArray } from "formik";
import { Form, Label, List, Icon } from "semantic-ui-react";
import _get from "lodash/get";
import { HTML5Backend } from "react-dnd-html5-backend";
import { DndProvider } from "react-dnd";
import { CreatibutorsModal } from "./CreatibutorsModal";
import { CreatibutorsFieldItem } from "./CreatibutorsFieldItem";
import { i18next } from "@translations/nr/i18next";
import { FieldDataProvider } from "@js/oarepo_ui";

const creatibutorNameDisplay = (value) => {
  const name = _get(value, `fullName`);

  return `${name}`;
};

class CreatibutorsFieldForm extends Component {
  handleOnContributorChange = (selectedCreatibutor) => {
    const { push: formikArrayPush } = this.props;
    formikArrayPush(selectedCreatibutor);
  };

  render() {
    const {
      form: { values, errors, initialErrors, initialValues },
      remove: formikArrayRemove,
      replace: formikArrayReplace,
      move: formikArrayMove,
      name: fieldPath,
      label,
      schema,
      modal,
      required,
      autocompleteNames,
      addButtonLabel,
      nameTypeHelpText,
      fieldPathPrefix,
    } = this.props;

    const creatibutorsList = getIn(values, fieldPath, []);
    const formikInitialValues = getIn(initialValues, fieldPath, []);

    const error = getIn(errors, fieldPath, null);
    const initialError = getIn(initialErrors, fieldPath, null);
    const creatibutorsError =
      error || (creatibutorsList === formikInitialValues && initialError);

    return (
      <FieldDataProvider fieldPathPrefix={fieldPathPrefix}>
        <DndProvider context={window} backend={HTML5Backend}>
          <Form.Field
            required={required}
            className={creatibutorsError ? "error" : ""}
          >
            {label}
            <List>
              {creatibutorsList.map((value, index) => {
                const key = `${fieldPath}.${index}`;
                const displayName = creatibutorNameDisplay(value);
                return (
                  <CreatibutorsFieldItem
                    key={key}
                    nameTypeHelpText={nameTypeHelpText}
                    {...{
                      displayName,
                      index,
                      schema,
                      compKey: key,
                      initialCreatibutor: value,
                      removeCreatibutor: formikArrayRemove,
                      replaceCreatibutor: formikArrayReplace,
                      moveCreatibutor: formikArrayMove,
                      addLabel: modal.addLabel,
                      editLabel: modal.editLabel,
                      autocompleteNames: autocompleteNames,
                    }}
                  />
                );
              })}
              <CreatibutorsModal
                key="add-creatibutor-modal"
                onCreatibutorChange={this.handleOnContributorChange}
                initialAction="add"
                addLabel={modal.addLabel}
                editLabel={modal.editLabel}
                schema={schema}
                nameTypeHelpText={nameTypeHelpText}
                autocompleteNames={autocompleteNames}
                trigger={
                  <Form.Button
                    type="button"
                    icon
                    labelPosition="left"
                    className="array-field-add-button inline-block"
                  >
                    <Icon name="add" />
                    {addButtonLabel}
                  </Form.Button>
                }
              />
              {creatibutorsError && typeof creatibutorsError == "string" && (
                <Label pointing="left" prompt>
                  {creatibutorsError}
                </Label>
              )}
            </List>
          </Form.Field>
        </DndProvider>
      </FieldDataProvider>
    );
  }
}

export class CreatibutorsField extends Component {
  render() {
    const { fieldPath } = this.props;

    return (
      <FieldArray
        name={fieldPath}
        render={(formikProps) => (
          <CreatibutorsFieldForm {...formikProps} {...this.props} />
        )}
      />
    );
  }
}

CreatibutorsFieldForm.propTypes = {
  addButtonLabel: PropTypes.string,
  modal: PropTypes.shape({
    addLabel: PropTypes.string.isRequired,
    editLabel: PropTypes.string.isRequired,
  }),
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  form: PropTypes.object.isRequired,
  remove: PropTypes.func.isRequired,
  replace: PropTypes.func.isRequired,
  move: PropTypes.func.isRequired,
  push: PropTypes.func.isRequired,
  name: PropTypes.string.isRequired,
  required: PropTypes.bool,
  nameTypeHelpText: PropTypes.string,
  fieldPathPrefix: PropTypes.string,
};

CreatibutorsFieldForm.defaultProps = {
  autocompleteNames: "search",
  label: i18next.t("Creators"),
  modal: {
    addLabel: i18next.t("Add creator"),
    editLabel: i18next.t("Edit creator"),
  },
  addButtonLabel: i18next.t("Add creator"),
  fieldPathPrefix: "",
};

CreatibutorsField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  addButtonLabel: PropTypes.string,
  modal: PropTypes.shape({
    addLabel: PropTypes.string.isRequired,
    editLabel: PropTypes.string.isRequired,
  }),
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  labelIcon: PropTypes.string,
  required: PropTypes.bool,
  nameTypeHelpText: PropTypes.string,
  fieldPathPrefix: PropTypes.string,
};

CreatibutorsField.defaultProps = {
  autocompleteNames: "search",
  label: undefined,
  labelIcon: undefined,
  modal: {
    addLabel: i18next.t("Add creator"),
    editLabel: i18next.t("Edit creator"),
  },
  addButtonLabel: i18next.t("Add creator"),
  fieldPathPrefix: "",
};
