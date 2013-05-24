from decimal import Decimal
from django.db.models import Count
from django.test import TestCase, LiveServerTestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from models import Ingredient, IngredientItem, Parent, Recipe, SIPParent, Batch, Sample, Product, ProductReview
from inventory.models import Jar
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys

# JMT: There's a whole lot of trusting-the-admin-site-output here.
# Nearly all these tests are testing for *success*, not for *accuracy*.


class SeleniumTestCase(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)
        super(SeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTestCase, cls).tearDownClass()

    def login_as_admin(self, url):
        userdict = {'username': 'admin',
                    'password': 'pbkdf2_sha256$10000$dMAdIm5LrBkt$gS8TSnpYq7J/YEbEeQ5AMr6AHOz/RHtHIapWHKjSHwM=',
                    'email': 'admin@example.com',
                    'is_superuser': True,
                    'is_staff': True,
                    }
        admin_user, created = User.objects.get_or_create(username=userdict['username'], defaults=userdict)
        self.selenium.get(self.live_server_url + url)
        username_field = self.selenium.find_element_by_name('username')
        username_field.send_keys(userdict['username'])
        password_field = self.selenium.find_element_by_name('password')
        password_field.send_keys('passw0rd')
        password_field.send_keys(Keys.RETURN)

    def pick_option(self, name, text):
        for option in self.selenium.find_element_by_name(name).find_elements_by_tag_name('option'):
            if option.text == text:
                option.click()

    def populate_object(self, fields={}, ingredients=[]):
        for key, value in fields.items():
            field = self.selenium.find_element_by_name(key)
            field.clear()
            field.send_keys(value)
        for index, ingredient in enumerate(ingredients):
            name, amount, temp = ingredient
            idhead = 'ingredientitem_set-%d' % index
            step = 0
            found = False
            while step < 10:
                try:
                    div = self.selenium.find_element_by_id(idhead)
                    found = True
                    break
                except NoSuchElementException:
                    step = step + 1
                    self.selenium.find_element_by_link_text('Add another Ingredient Item').click()
            self.assertTrue(found)
            self.pick_option('%s-ingredient' % idhead, name)
            amount_field = self.selenium.find_element_by_name('%s-amount' % idhead)
            amount_field.clear()
            amount_field.send_keys(amount)
            temp_field = self.selenium.find_element_by_name('%s-temp' % idhead)
            temp_field.clear()
            temp_field.send_keys(temp)


class ViewTest(TestCase):
    fixtures = ['meadery']

    def test_meadery_home(self):
        response = self.client.get(reverse('meadery_home'))
        self.assertEqual(response.status_code, 200)

    def test_meadery_category(self):
        try:
            data = Product.active.order_by().values_list('category').distinct('category')[0][0]
        except IndexError:
            self.fail('No active products found!')
        kwargs = {}
        kwargs['category_value'] = data
        response = self.client.get(reverse('meadery_category', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)

    def test_meadery_product(self):
        try:
            data = Product.active.order_by().values_list('slug')[0][0]
        except IndexError:
            self.fail('No active products found!')
        kwargs = {}
        kwargs['product_slug'] = data
        response = self.client.get(reverse('meadery_product', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)

    def test_product_add_review(self):
        # JMT: not exactly sure how to do this...
        pass


class IngredientTestCase(SeleniumTestCase):
    fixtures = ['meadery']

    def test_add(self):
        self.login_as_admin(reverse('admin:meadery_ingredient_add'))
        # Set boring fields.
        fields = {'name': 'Test Honey',
                  'appellation': '(None)',
                  'sg': '1.422',
                  'sh': '0.57',
                  'cpu': '7.95'}
        self.populate_object(fields)
        # JMT: is checking just the 'Sugar' case adequate?
        self.pick_option('type', 'Sugar')
        # Try saving with bad subtype values.
        bad_subtypes = ['Water', 'Spice', 'Dry']
        for subtype in bad_subtypes:
            self.pick_option('subtype', subtype)
            self.selenium.find_element_by_name('_save').click()
            self.assertIn('Ingredient type and subtype must match.', self.selenium.find_element_by_tag_name('body').text)
        # Try saving with bad state values.
        self.pick_option('subtype', 'Honey')
        bad_states = ['Liquid', 'Other']
        for state in bad_states:
            self.pick_option('state', state)
            self.selenium.find_element_by_name('_save').click()
            self.assertIn('Ingredient state does not match type.', self.selenium.find_element_by_tag_name('body').text)
        # Try saving with 'Sugar | Honey | Solid': succeed
        self.pick_option('state', 'Solid')
        self.selenium.find_element_by_name('_save').click()
        self.assertIn('The ingredient "%s" was added successfully.' % fields['name'], self.selenium.find_element_by_tag_name('body').text)

    def test_modify(self):
        try:
            ingredient = Ingredient.objects.all()[0]
        except IndexError:
            self.fail('No ingredients found!')
        pk = ingredient.pk
        name = ingredient.name
        self.login_as_admin(reverse('admin:meadery_ingredient_change', args=(pk,)))
        fields = {'sh': '1.00'}
        self.populate_object(fields)
        self.selenium.find_element_by_name('_save').click()
        self.assertIn('The ingredient "%s" was changed successfully.' % name, self.selenium.find_element_by_tag_name('body').text)

    def test_delete(self):
        try:
            ingredient = Ingredient.objects.all()[0]
        except IndexError:
            self.fail('No ingredients found!')
        pk = ingredient.pk
        name = ingredient.name
        self.login_as_admin(reverse('admin:meadery_ingredient_delete', args=(pk,)))
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('Are you sure?', body.text)
        self.assertIn('All of the following related items will be deleted', body.text)
        self.selenium.find_element_by_xpath('//input[@type="submit"]').click()
        self.assertIn('The ingredient "%s" was deleted successfully.' % name, self.selenium.find_element_by_tag_name('body').text)


class IngredientItemTestCase(TestCase):
    """
    For now I am testing ingredient items from within recipes.
    """
    pass


class RecipeTestCase(SeleniumTestCase):
    fixtures = ['meadery']

    def test_add(self):
        # JMT: eventually test for 'bad recipes', whatever that means
        # ... missing yeast?  missing water?  missing sugar?
        self.login_as_admin(reverse('admin:meadery_recipe_add'))
        # Set boring fields.
        fields = {'title': 'Test Recipe',
                  'description': 'Test description!'}
        # Set ingredients.
        ingredients = [['Local Honey', '4.540', '70'],
                       ['Local Water', '9.725', '140'],
                       ['Local Water', '9.725', '70'],
                       ['Red Star Champagne Yeast', '1', '100']]
        self.populate_object(fields, ingredients)
        self.selenium.find_element_by_name('_save').click()
        self.assertIn('The recipe "%s" was added successfully.' % fields['title'], self.selenium.find_element_by_tag_name('body').text)

    def test_delete(self):
        try:
            recipe = Recipe.objects.all()[0]
        except IndexError:
            self.fail('No recipe found!')
        pk = recipe.pk
        name = recipe.name
        self.login_as_admin(reverse('admin:meadery_recipe_delete', args=(pk,)))
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('Are you sure?', body.text)
        self.assertIn('All of the following related items will be deleted', body.text)
        # Yes, we are sure!
        self.selenium.find_element_by_xpath('//input[@type="submit"]').click()
        self.assertIn('The recipe "%s" was deleted successfully.' % name, self.selenium.find_element_by_tag_name('body').text)

    def test_modify(self):
        try:
            recipe = Recipe.objects.all()[0]
        except IndexError:
            self.fail('No recipe found!')
        pk = recipe.pk
        name = recipe.name
        self.login_as_admin(reverse('admin:meadery_recipe_change', args=(pk,)))
        fields = {'description': 'New Description'}
        self.populate_object(fields)
        self.selenium.find_element_by_name('_save').click()
        self.assertIn('The recipe "%s" was changed successfully.' % name, self.selenium.find_element_by_tag_name('body').text)

    def test_create_batch_from_recipe(self):
        try:
            recipe = Recipe.objects.all()[0]
        except IndexError:
            self.fail('No recipe found!')
        pk = recipe.pk
        name = recipe.name
        self.login_as_admin(reverse('admin:meadery_recipe_change', args=(pk,)))
        self.selenium.find_element_by_link_text('Create batch from recipe').click()
        self.assertIn('One batch was created!', self.selenium.find_element_by_tag_name('body').text)


class BatchTestCase(SeleniumTestCase):
    fixtures = ['meadery']

    def test_add_from_scratch(self):
        self.login_as_admin(reverse('admin:meadery_batch_add'))
        # Set boring fields.
        fields = {'title': 'Test Batch',
                  'description': 'Test description!',
                  'brewname': 'SIP 99',
                  'batchletter': 'A',
                  'event': 'Christmas',
                  'jars': '0'}
        ingredients = [['Local Honey', '4.540', '70'],
                       ['Local Water', '9.725', '140'],
                       ['Local Water', '9.725', '70'],
                       ['Red Star Champagne Yeast', '1', '100']]
        self.populate_object(fields, ingredients)
        self.selenium.find_element_by_name('_save').click()
        self.assertIn('The batch "%s %s" was added successfully.' % (fields['brewname'], fields['batchletter']), self.selenium.find_element_by_tag_name('body').text)

    def test_add_from_recipe(self):
        self.login_as_admin(reverse('admin:meadery_batch_add'))
        # Set boring fields.
        fields = {'title': 'Test Batch',
                  'description': 'Test description!',
                  'brewname': 'SIP 99',
                  'batchletter': 'A',
                  'event': 'Christmas',
                  'jars': '0'}
        try:
            recipe = Recipe.objects.all()[0].name
        except IndexError:
            self.fail('No recipe found!')
        self.pick_option('recipe', recipe)
        self.populate_object(fields)
        self.selenium.find_element_by_name('_save').click()
        self.assertIn('The batch "%s %s" was added successfully.' % (fields['brewname'], fields['batchletter']), self.selenium.find_element_by_tag_name('body').text)

    def test_delete_from_scratch_without_samples(self):
        try:
            batch = Batch.objects.annotate(num_samples=Count('sample')).filter(recipe__isnull=True, num_samples=0)[0]
        except IndexError:
            self.fail('There is no batch from scratch without samples in the fixture!')
        pk = batch.pk
        name = batch.name
        self.login_as_admin(reverse('admin:meadery_batch_delete', args=(pk,)))
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('Are you sure?', body.text)
        self.assertIn('All of the following related items will be deleted', body.text)
        # Yes, we are sure!
        self.selenium.find_element_by_xpath('//input[@type="submit"]').click()
        self.assertIn('The batch "%s" was deleted successfully.' % name, self.selenium.find_element_by_tag_name('body').text)

    def test_delete_from_scratch_with_samples(self):
        try:
            batch = Batch.objects.annotate(num_samples=Count('sample')).filter(recipe__isnull=True, num_samples__gt=0)[0]
        except IndexError:
            self.fail('There is no batch from scratch with samples in the fixture!')
        pk = batch.pk
        name = batch.name
        self.login_as_admin(reverse('admin:meadery_batch_delete', args=(pk,)))
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('Are you sure?', body.text)
        self.assertIn('All of the following related items will be deleted', body.text)
        # Yes, we are sure!
        self.selenium.find_element_by_xpath('//input[@type="submit"]').click()
        self.assertIn('The batch "%s" was deleted successfully.' % name, self.selenium.find_element_by_tag_name('body').text)

    def test_delete_from_recipe_without_samples(self):
        try:
            batch = Batch.objects.annotate(num_samples=Count('sample')).filter(recipe__isnull=False, num_samples=0)[0]
        except IndexError:
            self.fail('There is no batch from a recipe without samples in the fixture!')
        pk = batch.pk
        name = batch.name
        old_recipe_count = Recipe.objects.count()
        self.login_as_admin(reverse('admin:meadery_batch_delete', args=(pk,)))
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('Are you sure?', body.text)
        self.assertIn('All of the following related items will be deleted', body.text)
        # Yes, we are sure!
        self.selenium.find_element_by_xpath('//input[@type="submit"]').click()
        self.assertIn('The batch "%s" was deleted successfully.' % name, self.selenium.find_element_by_tag_name('body').text)
        new_recipe_count = Recipe.objects.count()
        self.assertEqual(old_recipe_count, new_recipe_count)

    def test_delete_from_recipe_with_samples(self):
        try:
            batch = Batch.objects.annotate(num_samples=Count('sample')).filter(recipe__isnull=False, num_samples__gt=0)[0]
        except IndexError:
            self.fail('There is no batch from a recipe with samples in the fixture!')
        pk = batch.pk
        name = batch.name
        old_recipe_count = Recipe.objects.count()
        self.login_as_admin(reverse('admin:meadery_batch_delete', args=(pk,)))
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('Are you sure?', body.text)
        self.assertIn('All of the following related items will be deleted', body.text)
        # Yes, we are sure!
        self.selenium.find_element_by_xpath('//input[@type="submit"]').click()
        self.assertIn('The batch "%s" was deleted successfully.' % name, self.selenium.find_element_by_tag_name('body').text)
        new_recipe_count = Recipe.objects.count()
        self.assertEqual(old_recipe_count, new_recipe_count)

    def test_modify(self):
        try:
            batch = Batch.objects.all()[0]
        except IndexError:
            self.fail('No batch found!')
        pk = batch.pk
        name = batch.name
        self.login_as_admin(reverse('admin:meadery_batch_change', args=(pk,)))
        fields = {'description': 'New Description'}
        self.populate_object(fields)
        self.selenium.find_element_by_name('_save').click()
        self.assertIn('The batch "%s" was changed successfully.' % name, self.selenium.find_element_by_tag_name('body').text)

    def test_create_recipe_from_batch(self):
        try:
            batch = Batch.objects.all()[0]
        except IndexError:
            self.fail('No batch found!')
        pk = batch.pk
        self.login_as_admin(reverse('admin:meadery_batch_change', args=(pk,)))
        self.selenium.find_element_by_link_text('Create recipe from batch').click()
        self.assertIn('One recipe was created!', self.selenium.find_element_by_tag_name('body').text)

    def test_create_product_from_batch_with_samples(self):
        try:
            batch = Batch.objects.annotate(num_samples=Count('sample')).filter(num_samples__gt=0)[0]
        except IndexError:
            self.fail('There is no batch with samples in the fixture!')
        # JMT: not testing for jars at the moment
        batch.jars = 24
        batch.save()
        pk = batch.pk
        self.login_as_admin(reverse('admin:meadery_batch_change', args=(pk,)))
        self.selenium.find_element_by_link_text('Create product from batch').click()
        self.assertIn('One product was created!', self.selenium.find_element_by_tag_name('body').text)

    def test_create_product_from_batch_without_samples(self):
        try:
            batch = Batch.objects.annotate(num_samples=Count('sample')).filter(num_samples=0)[0]
        except IndexError:
            self.fail('There is no batch without samples in the fixture!')
        # JMT: not testing for jars at the moment
        batch.jars = 24
        batch.save()
        pk = batch.pk
        self.login_as_admin(reverse('admin:meadery_batch_change', args=(pk,)))
        self.selenium.find_element_by_link_text('Create product from batch').click()
        self.assertIn('No product was created!', self.selenium.find_element_by_tag_name('body').text)

    def test_make_labels(self):
        # JMT: conventional wisdom on the internet says don't test file downloads
        pass


class SampleTestCase(SeleniumTestCase):
    fixtures = ['meadery']

    def test_add(self):
        self.login_as_admin(reverse('admin:meadery_sample_add'))
        fields = {'date': '2012-05-31',
                  'temp': '60',
                  'sg': '1.168',
                  'notes': 'Tastes great!'}
        self.populate_object(fields)
        try:
            batch = Batch.objects.all()[0].name
        except IndexError:
            self.fail('No batch found!')
        self.pick_option('batch', batch)
        self.selenium.find_element_by_name('_save').click()
        body = self.selenium.find_element_by_tag_name('body')
        # Figuring out the middle is annoying.
        self.assertIn('The sample ', body.text)
        self.assertIn('was added successfully.', body.text)

    def test_modify(self):
        try:
            sample = Sample.objects.all()[0]
        except IndexError:
            self.fail('No samples found!')
        pk = sample.pk
        name = sample.__unicode__()
        self.login_as_admin(reverse('admin:meadery_sample_change', args=(pk,)))
        fields = {'notes': 'Still delicious.'}
        self.populate_object(fields)
        self.selenium.find_element_by_name('_save').click()
        self.assertIn('The sample "%s" was changed successfully.' % name, self.selenium.find_element_by_tag_name('body').text)

    def test_delete(self):
        try:
            sample = Sample.objects.all()[0]
        except IndexError:
            self.fail('No samples found!')
        pk = sample.pk
        name = sample.__unicode__()
        old_batch_count = Batch.objects.count()
        self.login_as_admin(reverse('admin:meadery_sample_delete', args=(pk,)))
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('Are you sure?', body.text)
        self.assertIn('All of the following related items will be deleted', body.text)
        # Yes, we are sure!
        self.selenium.find_element_by_xpath('//input[@type="submit"]').click()
        self.assertIn('The sample "%s" was deleted successfully.' % name, self.selenium.find_element_by_tag_name('body').text)
        new_batch_count = Batch.objects.count()
        self.assertEqual(old_batch_count, new_batch_count)


class ProductTestCase(SeleniumTestCase):
    def test_add(self):
        self.login_as_admin(reverse('admin:meadery_product_add'))
        # Set boring fields.
        fields = {'title': 'Test Product',
                  'description': 'Test description!',
                  'brewname': 'SIP 99',
                  'batchletter': 'A',
                  'meta_keywords': 'bogus',
                  'meta_description': 'bogus',
                  'brewed_date': '2013-05-01',
                  'brewed_sg': '1.126',
                  'bottled_date': '2013-05-31',
                  'bottled_sg': '0.996',
                  'abv': '17.33'}
        self.populate_object(fields)
        self.pick_option('category', 'Dry Mead')
        self.selenium.find_element_by_name('_save').click()
        self.assertIn('The product "%s %s" was added successfully.' % (fields['brewname'], fields['batchletter']), self.selenium.find_element_by_tag_name('body').text)

    def test_delete(self):
        print Product.objects.all()
        try:
            product = Product.objects.annotate(num_jars=Count('jar')).filter(num_jars=0)[0]
        except IndexError:
            print [(product.name, product.num_jars) for product in Product.objects.annotate(num_jars=Count('jar')).all()]
            self.fail('No products without jars found!')
        pk = product.pk
        name = product.name
        old_batch_count = Batch.objects.count()
        self.login_as_admin(reverse('admin:meadery_product_delete', args=(pk,)))
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('Are you sure?', body.text)
        # We do not want to delete related objects!
        self.assertNotIn('All of the following related items will be deleted', body.text)
        self.selenium.find_element_by_xpath('//input[@type="submit"]').click()
        self.assertIn('The product "%s" was deleted successfully.' % name, self.selenium.find_element_by_tag_name('body').text)
        new_batch_count = Batch.objects.count()
        self.assertEqual(old_batch_count, new_batch_count)


class ProductReviewTestCase(SeleniumTestCase):
    """
    I do not know if I'm going to bother with this.
    """
    pass
