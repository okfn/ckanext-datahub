import re
import logging
import ckan.lib.helpers as h
import ckan.plugins as p

import ckan.lib.base as base
_ = base._


class PurgeCommand(p.toolkit.CkanCommand):
    '''Purge deleted datasets and revisions

    Usage::
        paster purge

    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0

    def command(self):
        self._load_config()
        self.purge()

    def purge_revs(self, revs_to_purge):
        import ckan.model as model
        for id in revs_to_purge:
            revision = model.Session.query(model.Revision).get(id)
            try:
                model.repo.purge_revision(revision, leave_record=False)
            except Exception, inst:
                msg = _('Problem purging revision %s: %s') % (id, inst)

    def purge(self):
        import ckan.model as model
        deleted_revisions = model.Session.query(
            model.Revision).filter_by(state=model.State.DELETED)
        deleted_packages = model.Session.query(
            model.Package).filter_by(state=model.State.DELETED)
        print "Processing deleted revisions"
        self.purge_revs([rev.id for rev in deleted_revisions])
        revs_to_purge = []
        for pkg in deleted_packages:
            print "Processing package %s" % (pkg.id)
            revisions = [x[0] for x in pkg.all_related_revisions]
            problem = False
            for r in revisions:
                affected_pkgs = set(
                    r.packages).difference(set(deleted_packages))
                if affected_pkgs:
                    msg = _('Cannot purge package %s as '
                            'associated revision %s includes '
                            'non-deleted packages %s')
                    print msg % (pkg.id, r.id, [pkg.id for r in affected_pkgs])
                    problem = True
                    break
            if not problem:
                print "Deleting %d revisions for package %s" % (
                    len(revisions), pkg.id)
                self.purge_revs([r.id for r in revisions])
            model.Session.remove()
        print (_('Purge complete'))
