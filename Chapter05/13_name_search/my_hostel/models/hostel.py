# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class HostelRoom(models.Model):

    _name = 'hostel.room'
    _description = "Information about hostel Room"

    name = fields.Char(string="Hostel Name", required=True)
    room_no = fields.Char(string="Room Number", required=True)
    other_info = fields.Text("Other Information",
                             help="Enter more information")
    description = fields.Html('Description')
    room_rating = fields.Float('Hostel Average Rating', digits=(14, 4))
    member_ids = fields.Many2many('hostel.room.member', string='Members')
    previous_room_id = fields.Many2one('hostel.room', string='Previous Room')
    state = fields.Selection([
        ('draft', 'Unavailable'),
        ('available', 'Available'),
        ('closed', 'Closed')],
        'State', default="draft")
    remarks = fields.Text('Remarks')

    @api.model
    def create(self, values):
        if not self.user_has_groups('my_hostel.group_hostel_manager'):
            values.get('remarks')
            if values.get('remarks'):
                raise UserError(
                    'You are not allowed to modify '
                    'remarks'
                )
        return super(HostelRoom, self).create(values)

    def write(self, values):
        if not self.user_has_groups('my_hostel.group_hostel_manager'):
            if values.get('remarks'):
                raise UserError(
                    'You are not allowed to modify '
                    'remarks'
                )
        return super(HostelRoom, self).write(values)

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
                   ('available', 'closed'),
                   ('closed', 'draft')]
        return (old_state, new_state) in allowed

    def change_state(self, new_state):
        for room in self:
            if room.is_allowed_transition(room.state, new_state):
                room.state = new_state
            else:
                message = _('Moving from %s to %s is not allowed') % (room.state, new_state)
                raise UserError(message)

    def make_available(self):
        self.change_state('available')

    def make_closed(self):
        self.change_state('closed')

    def name_get(self):
        result = []
        for room in self:
            members = room.member_ids.mapped('name')
            name = '%s (%s)' % (room.name, ', '.join(members))
            result.append((room.id, name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = [] if args is None else args.copy()
        if not(name == '' and operator == 'ilike'):
            args += ['|', '|', '|',
                ('name', operator, name),
                ('room_no', operator, name),
                ('member_ids.name', operator, name)
            ]
        return super(HostelRoom, self)._name_search(
            name=name, args=args, operator=operator,
            limit=limit, name_get_uid=name_get_uid)


class HostelRoomMember(models.Model):

    _name = 'hostel.room.member'
    _inherits = {'res.partner': 'partner_id'}
    _description = "Hostel Room member"

    partner_id = fields.Many2one('res.partner', ondelete='cascade')
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    member_code = fields.Integer()
    date_of_birth = fields.Date('Date of birth')

