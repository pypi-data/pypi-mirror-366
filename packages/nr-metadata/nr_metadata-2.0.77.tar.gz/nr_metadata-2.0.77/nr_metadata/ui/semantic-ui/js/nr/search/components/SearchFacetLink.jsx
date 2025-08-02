import React from "react";
import PropTypes from "prop-types";
import { Popup } from "semantic-ui-react";

export const SearchFacetLink = ({
  searchUrl = "/",
  searchFacet,
  value,
  title,
  label,
  className,
  ...rest
}) => (
  <Popup
    position="top center"
    content={`🔎 ${title}`}
    trigger={
      <a
        className={className}
        href={`${searchUrl}?q=&f=${searchFacet}:${encodeURI(value)}`}
        aria-label={title}
        {...rest}
      >
        <span className={`${className} label`}>{label || value}</span>
      </a>
    }
  />
);

SearchFacetLink.propTypes = {
  searchUrl: PropTypes.string,
  searchFacet: PropTypes.string.isRequired,
  value: PropTypes.string,
  title: PropTypes.string,
  label: PropTypes.string,
  className: PropTypes.string,
};
