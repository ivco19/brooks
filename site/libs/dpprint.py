import datetime as dt

from django.utils.html import format_html

class PPrinter:
    def __init_subclass__(cls, *a, **kw):
        cls._meta = cls.Meta
        del cls.Meta

    def __init__(self, instance):
        assert isinstance(instance, self._meta.model)
        self._inst = instance

    def iter_model(self):
        fields = {}
        for field in self._inst._meta.fields:
            if field.name in self._meta.exclude:
                continue
            value_obj = field.value_from_object(self._inst)

            fvname = field.verbose_name.replace("_", " ").title()

            fvalue = (
                "" if value_obj is None else
                field.value_to_string(self._inst))
            fields[field.name] = (fvname,  fvalue)

        for fname in self._meta.order:
            fvname, fvalue = fields.pop(fname)
            yield fvname, fvalue

        for fname, fdata in fields.items():
            fvname, fvalue = fdata
            yield fvname, fvalue

    def pprint(self):
        raise NotImplementedError()

    def to_html(self):
        return format_html(self.pprint())




class ULPPrinter(PPrinter):

    class Meta:
        abstract = True

    def get_template(self):
        return UL_TEMPLATE

    def pprint(self):
        parts = ["<ul class='pprint-ul'>"]
        for fname, fvalue in self.iter_model():
            if isinstance(fvalue, dt.datetime):
                fvalue = fvalue.isoformat()
            parts.append(f"<li><label>{fname}:</label> {fvalue}</li>")
        parts.append("</ul>")
        return "\n".join(parts)