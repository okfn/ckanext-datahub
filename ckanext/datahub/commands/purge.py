import re
import logging
import ckan.lib.helpers as h
import ckan.plugins as p

import ckan.lib.base as base
_ = base._


class PurgeCommand(p.toolkit.CkanCommand):
    '''Purge deleted datasets and revisions

    Usage::
        paster purge revisions Purge revisions marked for deletion
        paster purge datasets  Purge datasets marked for deletion
        paster purge all       Purge datasets and revisions marked for deletion
        paster purge list      Show datasets and revisions marked for deletion

    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 1
    min_args = 1

    def command(self):
        if not self.args or self.args[0] in ['--help', '-h', 'help'] or \
                not len(self.args) in [1, 2]:
            print self.usage
            return

        cmd = self.args[0]
        self._load_config()

        if cmd == 'revisions':
            self.purge_revs()
            print (_('Purge complete'))
        elif cmd == 'datasets':
            self.purge_packages()
            print (_('Purge complete'))
        elif cmd == 'all':
            self.purge_revs()
            self.purge_packages()
            print (_('Purge complete'))
        elif cmd == 'list':
            print "Deleted Revisions:"
            for rev in self.get_deleted_revisions():
                print "Revision %s" % (rev.id)
            print "Deleted Packages:"
            for pkg in self.get_deleted_packages():
                print "Package %s (%s)" % (pkg.id, pkg.name)
                for x in pkg.all_related_revisions:
                    print "Revision %s for package %s" % (
                        x[0].id, pkg.id)
        else:
            print 'Error: Command "{0}" not recognized'.format(cmd)
            print
            print self.usage

    def do_purge_revs(self, revs_to_purge):
        import ckan.model as model
        for id in revs_to_purge:
            revision = model.Session.query(model.Revision).get(id)
            try:
                model.repo.purge_revision(revision, leave_record=False)
            except Exception, inst:
                msg = _('Problem purging revision %s: %s') % (id, inst)

    def get_deleted_revisions(self):
        import ckan.model as model
        return model.Session.query(
            model.Revision).filter_by(state=model.State.DELETED)

    def get_deleted_packages(self):
        import ckan.model as model
        return model.Session.query(
            model.Package).filter_by(state=model.State.DELETED)

    def purge_revs(self):
        print "Processing deleted revisions"
        self.do_purge_revs([rev.id for rev in self.get_deleted_revisions()])

    def purge_packages(self):
        import ckan.model as model
        for pkg in self.get_deleted_packages():
            print "Processing package %s (%s)" % (pkg.id, pkg.name)
            revisions = [x[0] for x in model.Session.query(
                model.Package).get(pkg.id).all_related_revisions]
            problem = False
            for r in revisions:
                print "Processing revision %s for package %s" % (r.id, pkg.id)
                affected_pkgs = set(
                    r.packages).difference(set(self.get_deleted_packages()))
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
                self.do_purge_revs([r.id for r in revisions])
