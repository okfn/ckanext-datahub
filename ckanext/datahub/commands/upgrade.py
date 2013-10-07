import re
import logging
import ckan.lib.helpers as h
import ckan.plugins as p

class OrgUpgradeCommand(p.toolkit.CkanCommand):
    """

    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0

    def command(self):
        self._load_config()

        import ckan.model as model
        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)
        log = logging.getLogger()

        self.upgrade()

    def upgrade(self):
        import ckan.model as model

        u = p.toolkit.get_action('get_site_user')({'ignore_auth': True}, None)

        # If there is no Global Org, create it.
        glbl = model.Group.get('global')
        if not glbl:
            glbl = p.toolkit.get_action('organization_create')(
                {'user': u['name'], 'model': model, 'ignore_auth': True}, {'name': 'global','title': 'Global'})

        packages = model.Session.query(model.Package)\
            .filter(model.Package.state == 'active')

        count = 0

        matcher = re.compile("^[a-za-z].*[0-90-9]$")

        print "Processing %d package" % packages.count()
        for pkg in packages.all():
            if count == 0:
                rev = model.repo.new_revision()

            #
            if pkg.name.count(' ') + pkg.name.count('-') + pkg.name.count('_') == 0:
                if matcher.match(pkg.name):
                    #
                    # We should find the user, and state='delete' them too.
                    #
                    print "  Deleted probable spam", pkg.name
                    pkg.state == 'deleted'
                    model.Session.delete(pkg)
                    continue

            count = count + 1
            if count % 100 == 0:
                print "Up to ", count
                model.Session.commit()
                model.repo.commit_and_remove()
                rev = model.repo.new_revision()

            grps = pkg.get_groups('organization')
            if not grps:
                print "Adding %s to glbl" % pkg.name
                p.toolkit.get_action('package_owner_org_update')(
                    {'user': u['name'], 'model': model, 'ignore_auth': True},
                    {'id': pkg.id, 'organization_id': glbl.id })
            elif grps[0].name != 'global':
                # We have to pick a group, it'll have to be the first one.
                pkg.owner_org = grps[0].id
                try:
                    print "Adding %s to %s" % (pkg.name,grps[0].name)
                    model.Session.add(pkg)
                    model.Session.commit()
                    model.repo.commit_and_remove()
                except:
                    model.Session.rollback()
                    print "*" * 80
                    print "* Failed to process", pkg.name
                    print "*" * 80
                rev = model.repo.new_revision()
