// This file is part of React-Invenio-Deposit
// Copyright (C) 2020 CERN.
// Copyright (C) 2020 Northwestern University.
//
// React-Invenio-Deposit is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { Header, List } from "semantic-ui-react";
import { withState } from "react-searchkit";
import _get from "lodash/get";
import { FastField } from "formik";
import { getTitleFromMultilingualObject } from "@js/oarepo_ui";
import { i18next } from "@translations/nr/i18next";

export const LicenseResults = withState(
  ({ currentResultsState: results, serializeLicense, handleSubmit }) => {
    const serializeLicenseResult =
      serializeLicense ??
      ((result) => ({
        title: result.title,
        id: result.id,
      }));
    return (
      <FastField name="selectedLicense">
        {({ form: { values, setFieldValue } }) => (
          <List selection>
            {results.data.hits
              .filter((l) => l?.hierarchy?.leaf)
              .map((result) => {
                const { id, title, description } = result;
                return (
                  <List.Item
                    key={id}
                    onClick={() => {
                      setFieldValue(
                        "selectedLicense",
                        serializeLicenseResult(result)
                      );
                      handleSubmit();
                    }}
                    className="license-item mb-15"
                    active={_get(values, "selectedLicense.id", "") === id}
                  >
                    <List.Content>
                      <Header size="small">{title}</Header>
                      <p>
                        {getTitleFromMultilingualObject(description)}{" "}
                        {
                          <a
                            href={result?.relatedURI?.URL}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                          >
                            {i18next.t("Read more.")}
                          </a>
                        }
                      </p>
                    </List.Content>
                  </List.Item>
                );
              })}
          </List>
        )}
      </FastField>
    );
  }
);
