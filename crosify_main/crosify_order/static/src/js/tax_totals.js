import {TaxGroupComponent} from "@account/static/components/tax_totals/tax_totals";
import {patch} from "@web/core/utils/patch";

patch(TaxGroupComponent.prototype, {
    onChangeTipInput() {
        this.setState("disable"); // Disable the input
        const oldValue = this.props.taxGroup.tax_group_amount;
        let newValue;
        try {
            newValue = parseFloat(this.inputTax.el.value); // Get the new value
        } catch {
            this.inputTax.el.value = oldValue;
            this.setState("edit");
            return;
        }
        // The newValue can"t be equals to 0
        if (newValue === oldValue || newValue === 0) {
            this.setState("readonly");
            return;
        }
        this.props.taxGroup.tax_group_amount = newValue;

        this.props.onChangeTaxGroup({
            oldValue,
            newValue: newValue,
            taxGroupId: this.props.taxGroup.tax_group_id,
        });
    }
});