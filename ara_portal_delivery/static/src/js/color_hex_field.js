/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

/**
 * Simple Char-field widget storing a hex color (e.g. "#3AAED8"). Renders a
 * native <input type="color"> picker so users can pick *any* color, plus
 * the hex code itself, next to a small live preview swatch.
 */
export class ColorHexField extends Component {
    static template = "portal_delivery.ColorHexField";
    static props = { ...standardFieldProps };

    get value() {
        return this.props.record.data[this.props.name] || "#875A7B";
    }

    onColorInput(ev) {
        this.props.record.update({ [this.props.name]: ev.target.value });
    }

    onTextInput(ev) {
        let val = ev.target.value.trim();
        if (val && !val.startsWith("#")) {
            val = "#" + val;
        }
        this.props.record.update({ [this.props.name]: val });
    }
}

export const colorHexField = {
    component: ColorHexField,
    supportedTypes: ["char"],
};

registry.category("fields").add("color_hex", colorHexField);
