from marshmallow import Schema, fields


class AlbumSchema(Schema):
    id = fields.Int()
    created_on = fields.DateTime()
    create_by = fields.Str()
    modified_on = fields.DateTime()
    modified_by = fields.Str()
    parent_id = fields.Int()
    cover_photo_id = fields.Int()
    sort_order = fields.Int()
    title = fields.Str()
    slug = fields.Str()


class PhotoSchema(Schema):
    id = fields.Int()
    created_on = fields.DateTime()
    create_by = fields.Str()
    modified_on = fields.DateTime()
    modified_by = fields.Str()
    album_id = fields.Int()
    title = fields.Str()
    slug = fields.Str()
    caption = fields.Str()
    original_filename = fields.Str()
    created_at = fields.DateTime()
    camera_make = fields.Str()
    camera_model = fields.Str()
    lens = fields.Str()
    focal_length = fields.Str()
    exposure = fields.Str()
    f_stop = fields.Str()
    height = fields.Str()
    width = fields.Str()
