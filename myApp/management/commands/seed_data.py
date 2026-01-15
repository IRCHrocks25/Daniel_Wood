"""
Management command to seed initial data
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myApp.models import Course, Lesson, Module
import re
import json
import uuid
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seed initial data for the learning platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--course-slug',
            type=str,
            help='Slug of the course to add lessons to (if not provided, will use or create default course)',
        )

    def generate_slug(self, title):
        """Generate a URL-friendly slug from a title"""
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special characters
        slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces and multiple dashes with single dash
        slug = slug.strip('-')                # Remove leading/trailing dashes
        # Truncate to 200 characters to match model max_length
        if len(slug) > 200:
            slug = slug[:200].rstrip('-')
        return slug
    
    def create_block(self, block_type, data, block_id=None):
        """Create an Editor.js block"""
        return {
            "id": block_id or str(uuid.uuid4()),
            "type": block_type,
            "data": data
        }
    
    def create_content_blocks(self, content_sections):
        """Create Editor.js blocks from content sections"""
        blocks = []
        for section in content_sections:
            if section['type'] == 'paragraph':
                blocks.append(self.create_block('paragraph', {'text': section['text']}))
            elif section['type'] == 'header':
                blocks.append(self.create_block('header', {
                    'text': section['text'],
                    'level': section.get('level', 2)
                }))
            elif section['type'] == 'list':
                blocks.append(self.create_block('list', {
                    'style': section.get('style', 'unordered'),
                    'items': section['items']
                }))
            elif section['type'] == 'quote':
                blocks.append(self.create_block('quote', {
                    'text': section['text'],
                    'caption': section.get('caption', '')
                }))
        
        return {
            "time": int(timezone.now().timestamp() * 1000),
            "blocks": blocks,
            "version": "2.28.2"
        }

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin.username}'))
        else:
            self.stdout.write('Admin user already exists')
        
        # Get or create course
        course_slug = options.get('course_slug') or 'asset-mastery'
        course, created = Course.objects.get_or_create(
            slug=course_slug,
            defaults={
                'name': 'Asset Mastery',
                'course_type': 'sprint',
                'status': 'active',
                'visibility': 'public',
                'enrollment_method': 'open',
                'description': '''Master the financial principles that separate the wealthy from everyone else. This comprehensive course reveals the money flow patterns, asset classes, and strategic frameworks used by high-net-worth individuals to build lasting wealth.

Learn how to structure your finances for freedom, understand the complete asset universe, and make intelligent investment decisions across real estate, stocks, bonds, commodities, precious metals, and cryptocurrency. This isn't about get-rich-quick schemes—it's about building a financial foundation that creates time, options, and true independence.

Transform your relationship with money and discover how the wealthy think differently about assets, income, and financial freedom.''',
                'short_description': 'Master the money flow patterns and asset strategies that create true wealth and financial freedom',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created course: {course.name}'))
        else:
            self.stdout.write(f'Course already exists: {course.name}')
        
        # Asset Mastery Course Lessons with full content
        lessons_data = [
            {
                'title': 'Asset Mastery: The Money Flow That Separates the Wealthy from Everyone Else',
                'order': 1,
                'description': "Most people believe wealth is about how much money you make. That belief quietly keeps them stuck forever. In this lesson, you'll discover why income doesn't create wealth — structure does, and how a single change in how your money flows can completely alter your financial future.",
                'google_drive_url': 'https://drive.google.com/file/d/1iAjnD-YM35aW2MBcRwacI1nYalnQ5P6u/view',
                'content_sections': [
                    {'type': 'paragraph', 'text': 'Welcome to Asset Mastery.'},
                    {'type': 'paragraph', 'text': "Before we talk about real estate, stocks, crypto, or any \"exciting\" investments, we need to start with something far more powerful — how money actually moves through your life."},
                    {'type': 'paragraph', 'text': "Because here's the uncomfortable truth:"},
                    {'type': 'paragraph', 'text': 'Two people can earn the exact same income and end up in completely different financial realities.'},
                    {'type': 'paragraph', 'text': 'One builds freedom. The other builds stress.'},
                    {'type': 'paragraph', 'text': "The difference isn't luck. It isn't intelligence. It's money flow."},
                    {'type': 'header', 'text': 'Why Most People Start in the Wrong Place', 'level': 2},
                    {'type': 'paragraph', 'text': 'A common question Daniel gets is:'},
                    {'type': 'quote', 'text': "\"If you were starting again at 23, what would you invest in first?\"", 'caption': ''},
                    {'type': 'paragraph', 'text': 'That sounds like a smart question — but it hides a deeper misunderstanding.'},
                    {'type': 'paragraph', 'text': 'What people are really asking is:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'What asset will save me time?',
                        'What shortcut gets me ahead faster?'
                    ]},
                    {'type': 'paragraph', 'text': 'The hard truth? No asset can save you if your financial foundation is broken.'},
                    {'type': 'paragraph', 'text': "That's why we start here."},
                    {'type': 'header', 'text': 'The Financial Statement Most Adults Have Never Truly Understood', 'level': 2},
                    {'type': 'paragraph', 'text': "Let's break down the Cashflow 101 Financial Statement, created by Robert and Kim Kiyosaki — not as an academic exercise, but as a mirror."},
                    {'type': 'paragraph', 'text': 'This statement has four parts:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Income – money coming in',
                        'Expenses – money going out',
                        'Assets – things that put money into your pocket',
                        'Liabilities – things that take money out of your pocket'
                    ]},
                    {'type': 'paragraph', 'text': 'Simple? Yes. Powerful? Life-changing.'},
                    {'type': 'paragraph', 'text': 'Because once you see this clearly, you can never unsee it.'},
                    {'type': 'header', 'text': 'The Three Money Patterns That Define Almost Everyone', 'level': 2},
                    {'type': 'header', 'text': '1. The "Poor" Pattern (Mindset, not income)', 'level': 3},
                    {'type': 'paragraph', 'text': 'Money comes in → Money goes out → Nothing remains.'},
                    {'type': 'paragraph', 'text': "It doesn't matter whether this person earns little or a lot — their money exists only to be spent. Lifestyle expands to match income, and the game resets every month."},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'No buffer.',
                        'No leverage.',
                        'No future momentum.'
                    ]},
                    {'type': 'header', 'text': '2. The Middle-Class Trap', 'level': 3},
                    {'type': 'paragraph', 'text': 'This is where most people live.'},
                    {'type': 'paragraph', 'text': 'Money comes in → Money goes into liabilities → Then expenses are paid → Nothing meaningful is left.'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Bigger house.',
                        'Nicer car.',
                        'More subscriptions.',
                        'More debt.'
                    ]},
                    {'type': 'paragraph', 'text': "On paper, it looks successful. On the balance sheet, it's fragile."},
                    {'type': 'paragraph', 'text': 'This is the life where:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'One missed paycheck causes panic',
                        'Freedom always feels "a few years away"',
                        'Retirement becomes a hope, not a plan'
                    ]},
                    {'type': 'header', 'text': '3. The Wealthy Pattern', 'level': 3},
                    {'type': 'paragraph', 'text': "Here's where everything changes."},
                    {'type': 'paragraph', 'text': 'Money comes in → Money goes into assets first → Assets generate income → Income pays for expenses.'},
                    {'type': 'paragraph', 'text': 'This person may look ordinary at first — but behind the scenes, they are quietly building machines that produce cash.'},
                    {'type': 'paragraph', 'text': 'Eventually:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Assets replace income',
                        'Work becomes optional',
                        'Time becomes abundant'
                    ]},
                    {'type': 'paragraph', 'text': "This isn't magic. It's math + discipline."},
                    {'type': 'header', 'text': 'The One Line That Changes Everything', 'level': 2},
                    {'type': 'paragraph', 'text': 'The entire difference between middle-class and wealthy lives comes down to one line on the financial statement.'},
                    {'type': 'paragraph', 'text': 'Most people send surplus money to:'},
                    {'type': 'paragraph', 'text': 'Liabilities → expenses → gone'},
                    {'type': 'paragraph', 'text': 'The wealthy redirect that same money to:'},
                    {'type': 'paragraph', 'text': 'Assets → income → freedom'},
                    {'type': 'paragraph', 'text': "That's it. That's the code."},
                    {'type': 'paragraph', 'text': 'Once you move that line — even slightly — momentum starts working for you instead of against you.'},
                    {'type': 'header', 'text': 'Why This Is About Freedom (Not Greed)', 'level': 2},
                    {'type': 'paragraph', 'text': "Assets aren't about yachts or status."},
                    {'type': 'paragraph', 'text': 'Assets buy:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Time',
                        'Options',
                        'Peace of mind',
                        'The ability to say no'
                    ]},
                    {'type': 'paragraph', 'text': 'When money works for you:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'You choose how to spend your days',
                        'You choose what problems to solve',
                        'You choose the life you actually want'
                    ]},
                    {'type': 'paragraph', 'text': "That's the real return on investment."},
                    {'type': 'header', 'text': 'Your First Action Step', 'level': 2},
                    {'type': 'paragraph', 'text': 'Before moving on:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Download the financial statement',
                        'Write down your real numbers',
                        'No judgment — just honesty'
                    ]},
                    {'type': 'paragraph', 'text': "This isn't about shame. It's about clarity."},
                    {'type': 'paragraph', 'text': 'Because clarity is where power begins.'},
                    {'type': 'header', 'text': 'What Comes Next', 'level': 2},
                    {'type': 'paragraph', 'text': 'Now that you understand how money should flow, the next logical question becomes:'},
                    {'type': 'quote', 'text': "\"Okay — what assets should I actually build?\"", 'caption': ''},
                    {'type': 'paragraph', 'text': "That's exactly where we're going next."},
                    {'type': 'paragraph', 'text': 'And this is where the gold mine starts revealing itself.'},
                ]
            },
            {
                'title': 'The Asset Universe: Where Wealth Actually Comes From',
                'order': 2,
                'description': "Most people never build wealth because they don't realize how many paths are available. In this lesson, you'll see the full landscape of investable assets — and understand why wealth isn't about choosing \"the best\" one, but choosing the right one for you.",
                'google_drive_url': 'https://drive.google.com/file/d/17jH7BlryFVv8RRSvlyKRLXuOn-qyONU2/view',
                'content_sections': [
                    {'type': 'paragraph', 'text': "Now that you understand how money should flow, the next question becomes obvious:"},
                    {'type': 'quote', 'text': 'Where do I send it?', 'caption': ''},
                    {'type': 'paragraph', 'text': "Most people never get a clear answer to this — which is why they either:"},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Do nothing',
                        'Follow hype',
                        "Or copy someone else's strategy without understanding it"
                    ]},
                    {'type': 'paragraph', 'text': 'This lesson exists to give you context, not instructions.'},
                    {'type': 'header', 'text': 'Why There Is No "Best" Asset', 'level': 2},
                    {'type': 'paragraph', 'text': 'There is no single best investment.'},
                    {'type': 'paragraph', 'text': 'There is only:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Best for your time horizon',
                        'Best for your risk tolerance',
                        'Best for your skills and interest',
                        'Best for your current stage of life'
                    ]},
                    {'type': 'paragraph', 'text': "Wealthy people don't obsess over one asset. They understand categories — and how each plays a role."},
                    {'type': 'header', 'text': 'The Major Asset Classes Explained Simply', 'level': 2},
                    {'type': 'header', 'text': 'Real Estate', 'level': 3},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Physical property',
                        'Can produce monthly cash flow',
                        'Often appreciates over time',
                        'Highly tax-efficient if structured well'
                    ]},
                    {'type': 'paragraph', 'text': 'Think of real estate as slow, heavy, powerful machinery.'},
                    {'type': 'header', 'text': 'Stocks & Shares', 'level': 3},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Ownership in businesses',
                        'Value grows as companies grow',
                        'Can pay dividends',
                        'Extremely liquid (easy to buy and sell)'
                    ]},
                    {'type': 'paragraph', 'text': 'Stocks are owning slices of the global economy.'},
                    {'type': 'header', 'text': 'Bonds', 'level': 3},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'You are the lender',
                        'Predictable returns',
                        'Lower risk, lower reward',
                        'Excellent for stability and timing'
                    ]},
                    {'type': 'paragraph', 'text': 'Bonds are financial shock absorbers.'},
                    {'type': 'header', 'text': 'Commodities', 'level': 3},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Raw materials that power the world',
                        'Food, energy, metals',
                        'Strong inflation hedge',
                        'Influenced by global supply chains'
                    ]},
                    {'type': 'paragraph', 'text': 'Commodities are real-world demand made tradable.'},
                    {'type': 'header', 'text': 'Precious Metals', 'level': 3},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Store of value',
                        'Hedge against uncertainty',
                        'Thousands of years of trust'
                    ]},
                    {'type': 'paragraph', 'text': 'Metals are wealth preservation tools.'},
                    {'type': 'header', 'text': 'Cryptocurrency', 'level': 3},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Digital assets',
                        'Decentralized systems',
                        'High upside, high volatility',
                        'Requires education and discipline'
                    ]},
                    {'type': 'paragraph', 'text': 'Crypto is early-stage financial infrastructure.'},
                    {'type': 'header', 'text': 'Funds & Indexes', 'level': 3},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Bundles of assets',
                        'Automatic diversification',
                        'Lower effort, steady growth'
                    ]},
                    {'type': 'paragraph', 'text': 'Funds are wealth-building on autopilot.'},
                    {'type': 'header', 'text': 'The Real Goal of This Lesson', 'level': 2},
                    {'type': 'paragraph', 'text': 'Not to overwhelm you.'},
                    {'type': 'paragraph', 'text': 'But to make you realize:'},
                    {'type': 'quote', 'text': "\"I don't need to do everything — I just need to start somewhere.\"", 'caption': ''},
                    {'type': 'paragraph', 'text': 'And now, instead of guessing, you get to choose intelligently.'},
                ]
            },
            {
                'title': 'Real Estate: The Asset That Pays You While You Sleep',
                'order': 3,
                'description': 'Real estate is one of the few assets that can pay your bills, grow in value, and protect you from inflation — all at the same time. But done wrong, it can also be brutal. This lesson shows you both sides.',
                'google_drive_url': 'https://drive.google.com/file/d/1xW71ra7LS7KJ-6-0gXi7kh0YtWyV2Qf5/view',
                'content_sections': [
                    {'type': 'paragraph', 'text': 'Real estate is powerful because it does two jobs at once:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'It appreciates over time',
                        'It generates cash flow'
                    ]},
                    {'type': 'paragraph', 'text': 'Most assets do only one.'},
                    {'type': 'header', 'text': 'Why Property Has Created So Many Fortunes', 'level': 2},
                    {'type': 'paragraph', 'text': 'When you rent out a property:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Tenants pay your mortgage',
                        'Inflation raises rents',
                        'The asset increases in value',
                        'Debt shrinks while equity grows'
                    ]},
                    {'type': 'paragraph', 'text': 'This is called leverage working in your favor.'},
                    {'type': 'header', 'text': 'Why Real Estate Is Not "Easy Money"', 'level': 2},
                    {'type': 'paragraph', 'text': "What people don't talk about:"},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Bad tenants',
                        'Repairs',
                        'Legal issues',
                        'Poor locations',
                        'Bad deal structures'
                    ]},
                    {'type': 'paragraph', 'text': "Daniel's £400,000 loss wasn't from property itself — it was from bad guidance."},
                    {'type': 'paragraph', 'text': 'Lesson:'},
                    {'type': 'quote', 'text': "Property doesn't forgive ignorance.", 'caption': ''},
                    {'type': 'header', 'text': 'The Hidden Advantage of Real Estate', 'level': 2},
                    {'type': 'paragraph', 'text': "It's a team sport."},
                    {'type': 'paragraph', 'text': 'You can outsource:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Management',
                        'Repairs',
                        'Leasing',
                        'Accounting'
                    ]},
                    {'type': 'paragraph', 'text': "You don't need to do everything — you need to structure correctly."},
                    {'type': 'header', 'text': 'When Real Estate Makes Sense', 'level': 2},
                    {'type': 'paragraph', 'text': 'Real estate works best when:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'You want stable cash flow',
                        'You think long-term',
                        'You have good mentorship',
                        'You understand your numbers'
                    ]},
                    {'type': 'paragraph', 'text': 'Done right, it becomes a financial engine.'},
                ]
            },
            {
                'title': "The Stock Market: Owning the World's Best Businesses",
                'order': 4,
                'description': "The stock market isn't gambling — it's ownership. This lesson reframes stocks from \"charts and numbers\" into what they truly are: pieces of real businesses creating real value.",
                'google_drive_url': 'https://drive.google.com/file/d/1dWb8HQxwib1tj_v0QfzeygsX-mH2Jziq/view',
                'content_sections': [
                    {'type': 'paragraph', 'text': 'Every stock represents:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'A company',
                        'With customers',
                        'Making products',
                        'Solving problems'
                    ]},
                    {'type': 'paragraph', 'text': 'When you buy a stock, you buy ownership, not a lottery ticket.'},
                    {'type': 'header', 'text': 'Why the Stock Market Exists', 'level': 2},
                    {'type': 'paragraph', 'text': 'It was created so companies could:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Raise capital',
                        'Share risk',
                        'Grow faster'
                    ]},
                    {'type': 'paragraph', 'text': 'Investors win when companies win. Losses are shared. Gains are shared.'},
                    {'type': 'header', 'text': 'How Wealth Is Built in Stocks', 'level': 2},
                    {'type': 'paragraph', 'text': 'Stocks build wealth through:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Capital appreciation – shares increase in value',
                        'Dividends – profits paid to owners'
                    ]},
                    {'type': 'paragraph', 'text': 'This is how Warren Buffett compounded wealth for decades.'},
                    {'type': 'header', 'text': 'The Real Risk in Stocks', 'level': 2},
                    {'type': 'paragraph', 'text': "The biggest danger isn't volatility."},
                    {'type': 'paragraph', 'text': "It's:"},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Buying without understanding',
                        'Emotional decisions',
                        'No strategy',
                        'No patience'
                    ]},
                    {'type': 'paragraph', 'text': 'Education turns risk into calculated probability.'},
                ]
            },
            {
                'title': 'Bonds: The Quiet Power Behind Smart Portfolios',
                'order': 5,
                'description': "Bonds don't make headlines — but they quietly protect and amplify intelligent portfolios. This lesson explains why experienced investors never ignore them.",
                'google_drive_url': 'https://drive.google.com/file/d/16zQ1WNQaea4fhBk7SAjLJ6f-T2V5EdT3/view',
                'content_sections': [
                    {'type': 'paragraph', 'text': 'Bonds are loans where you are the bank.'},
                    {'type': 'paragraph', 'text': 'Governments and corporations borrow. You earn interest.'},
                    {'type': 'header', 'text': 'Why Professionals Love Bonds', 'level': 2},
                    {'type': 'paragraph', 'text': 'Bonds:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Reduce volatility',
                        'Preserve capital',
                        'Create timing opportunities'
                    ]},
                    {'type': 'paragraph', 'text': 'When markets fall, bonds give you dry powder.'},
                    {'type': 'header', 'text': 'The Strategic Role of Bonds', 'level': 2},
                    {'type': 'paragraph', 'text': 'They allow you to:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Earn while waiting',
                        'Buy assets when prices drop',
                        'Sleep better during chaos'
                    ]},
                    {'type': 'paragraph', 'text': 'Not exciting — but extremely effective.'},
                ]
            },
            {
                'title': "Commodities: Profiting From the World's Needs",
                'order': 6,
                'description': 'Food, energy, and materials move the planet. This lesson shows how those necessities become investable opportunities.',
                'google_drive_url': 'https://drive.google.com/file/d/1Ges3rP3vRX-yO4Gh_gpJknJLQXp2BTml/view',
                'content_sections': [
                    {'type': 'paragraph', 'text': 'Commodities exist because:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'People always need food',
                        'Economies always need energy',
                        'Supply is never guaranteed'
                    ]},
                    {'type': 'header', 'text': 'Why Futures Exist', 'level': 2},
                    {'type': 'paragraph', 'text': 'They create certainty in an uncertain world:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Farmers lock prices',
                        'Buyers lock costs',
                        'Investors step in between'
                    ]},
                    {'type': 'paragraph', 'text': "You're trading expectations of the future."},
                    {'type': 'header', 'text': 'Who Commodities Are For', 'level': 2},
                    {'type': 'paragraph', 'text': 'Best suited for:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Macro thinkers',
                        'Inflation hedgers',
                        'Portfolio diversifiers'
                    ]},
                    {'type': 'paragraph', 'text': 'Complex — but powerful.'},
                ]
            },
            {
                'title': 'Precious Metals: Insurance for Your Wealth',
                'order': 7,
                'description': "Gold doesn't grow — it protects. This lesson explains why serious investors keep metals in their portfolios even when markets are booming.",
                'google_drive_url': 'https://drive.google.com/file/d/1sLz3D7QfaI_4gsFyJ2KKCO8yXGcNGh_2/view',
                'content_sections': [
                    {'type': 'paragraph', 'text': 'Gold has survived:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Empires',
                        'Wars',
                        'Currencies',
                        'Financial collapses'
                    ]},
                    {'type': 'paragraph', 'text': "That's not hype — that's history."},
                    {'type': 'header', 'text': 'Why Metals Matter', 'level': 2},
                    {'type': 'paragraph', 'text': 'They:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Preserve purchasing power',
                        'Hedge uncertainty',
                        'Balance risk'
                    ]},
                    {'type': 'paragraph', 'text': "They're not about speed — they're about stability."},
                ]
            },
            {
                'title': 'Cryptocurrency: The New Financial Frontier',
                'order': 8,
                'description': 'Crypto is volatile, misunderstood, and powerful. This lesson strips away hype and explains what crypto really is — and why it matters.',
                'google_drive_url': 'https://drive.google.com/file/d/1fJE2zdQ9-Nd3PN3ZBwq0Ut6LY5GaZQq9/view',
                'content_sections': [
                    {'type': 'paragraph', 'text': 'Crypto exists because:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Money loses value',
                        'Systems are centralized',
                        'Trust is fragile'
                    ]},
                    {'type': 'paragraph', 'text': 'Bitcoin introduced digital scarcity.'},
                    {'type': 'header', 'text': 'Why Some Crypto Succeeds (and Most Fail)', 'level': 2},
                    {'type': 'paragraph', 'text': 'Value comes from:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Utility',
                        'Adoption',
                        'Infrastructure',
                        'Trust'
                    ]},
                    {'type': 'paragraph', 'text': 'Meme coins fade. Platforms endure.'},
                    {'type': 'header', 'text': 'The Opportunity & The Danger', 'level': 2},
                    {'type': 'paragraph', 'text': 'Crypto can:'},
                    {'type': 'list', 'style': 'unordered', 'items': [
                        'Multiply wealth',
                        'Destroy capital'
                    ]},
                    {'type': 'paragraph', 'text': 'Knowledge is the difference.'},
                    {'type': 'header', 'text': 'Final Takeaway', 'level': 2},
                    {'type': 'paragraph', 'text': 'You now see the entire chessboard.'},
                    {'type': 'paragraph', 'text': "The goal isn't to master everything — It's to start building assets intentionally."},
                    {'type': 'paragraph', 'text': 'This is how wealth stops being mysterious and starts becoming inevitable.'},
                ]
            },
        ]
        
        # Create lessons
        for lesson_data in lessons_data:
            # Convert content sections to Editor.js blocks if provided
            content = {}
            if 'content_sections' in lesson_data:
                content = self.create_content_blocks(lesson_data['content_sections'])
            elif 'content' in lesson_data:
                content = lesson_data['content']
            
            slug = self.generate_slug(lesson_data['title'])
            lesson, created = Lesson.objects.get_or_create(
                course=course,
                slug=slug,
                defaults={
                    'title': lesson_data['title'],
                    'order': lesson_data['order'],
                    'description': lesson_data['description'],
                    'content': content,
                    'google_drive_url': lesson_data['google_drive_url'],
                    'lesson_type': 'video',
                    'video_duration': 0,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created lesson: {lesson.title}'))
                # Log content info
                if content and content.get('blocks'):
                    self.stdout.write(self.style.SUCCESS(f'    ✓ Content: {len(content.get("blocks", []))} blocks'))
            else:
                # Update existing lesson
                updated = False
                if lesson.google_drive_url != lesson_data['google_drive_url']:
                    lesson.google_drive_url = lesson_data['google_drive_url']
                    updated = True
                if lesson.description != lesson_data['description']:
                    lesson.description = lesson_data['description']
                    updated = True
                # Always update content if provided (to ensure it's saved)
                if content and content.get('blocks'):
                    lesson.content = content
                    updated = True
                    self.stdout.write(self.style.SUCCESS(f'    ✓ Updated content: {len(content.get("blocks", []))} blocks'))
                if updated:
                    lesson.save()
                    self.stdout.write(self.style.WARNING(f'  Updated lesson: {lesson.title}'))
                else:
                    self.stdout.write(f'  Lesson already exists: {lesson.title}')
        
        self.stdout.write(self.style.SUCCESS(f'\nSeeding completed! Created/updated {len(lessons_data)} lessons for course: {course.name}'))
