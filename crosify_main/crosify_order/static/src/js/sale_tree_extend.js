/** @odoo-module */
import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
export class SaleListController extends ListController {
   setup() {
       super.setup();
   }
   OnClickOpenImportFile() {
       this.actionService.doAction({
          type: 'ir.actions.act_window',
          res_model: 'update.link.design.wizard',
          name:'Update Link Design',
          view_mode: 'form',
          view_type: 'form',
          views: [[false, 'form']],
          target: 'new',
          res_id: false,
      });
   }
}
registry.category("views").add("button_in_tree", {
   ...listView,
   Controller: SaleListController,
   buttonTemplate: "crosify_order.ListView.Buttons",
});