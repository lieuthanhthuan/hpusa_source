openerp.hpusa_loyalty = function (instance) {
	   var _t = instance.web._t,
       _lt = instance.web._lt;
   var QWeb = instance.web.qweb;
   
   instance.web.loyalty = instance.web.loyalty || {};

   instance.web.views.add('tree_loyaty_quickadd', 'instance.web.loyalty.QuickAddListView');
   instance.web.loyalty.QuickAddListView = instance.web.ListView.extend({
       init: function() {
           this._super.apply(this, arguments);
           
       },
       start:function(){
           var tmp = this._super.apply(this, arguments);
           var self = this;
           var defs = [];
           
           this.$el.parent().prepend(QWeb.render("LoyaltyQuickAdd", {widget: this})); 
           this.$el.parent().find('.oe_loyalty_select_period').change(function() {
                   self.current_option = this.value === '' ? null : parseInt(this.value);
                   self.do_search(self.last_domain, self.last_context, self.last_group_by);
               });
           var mod = new instance.web.Model("hpusa.loyalty.report.1", self.dataset.context, self.dataset.domain);
           defs.push(mod.call("default_get", [['option'],self.dataset.context]).then(function(result) {
               self.current_option = result['option'];
           }));
           this.on('edit:after', this, function () {
               self.$el.parent().find('.oe_loyalty_select_period').attr('disabled', 'disabled');
           });
           this.on('save:after cancel:after', this, function () {
               self.$el.parent().find('.oe_loyalty_select_period').removeAttr('disabled');
           });
           return $.when(tmp, defs);
       },
       do_search: function(domain, context, group_by) {
           var self = this;
           var o;
           this.last_group_by = group_by;
           this.last_context = context;
           this.last_domain = domain;
           this.old_search = _.bind(this._super, this);
           if (self.current_option == null) self.current_option = '1';
           self.$el.parent().find('.oe_loyalty_select_period').children().remove().end();
           self.$el.parent().find('.oe_loyalty_select_period').append(new Option('All', '0'));
           o = new Option('Reward Card Issue', '1');
           self.$el.parent().find('.oe_loyalty_select_period').append(o); 
           
           o = new Option('Reward Point', '2');
           self.$el.parent().find('.oe_loyalty_select_period').append(o); 
           self.$el.parent().find('.oe_loyalty_select_period').val(self.current_option).attr('selected',true);
           return self.search_by_option();
       },
       search_by_option: function() {
           var self = this;
           var domain = [];
           self.last_context["option"] =  self.current_option;
           if (self.current_option !== null && self.current_option !== '0') domain.push(["option", "=", self.current_option]);
           if (self.current_option !== null && self.current_option == '0') domain = [];
           var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
           self.dataset.domain = compound_domain.eval();
           return self.old_search(compound_domain, self.last_context, self.last_group_by);
       },
   });
}
