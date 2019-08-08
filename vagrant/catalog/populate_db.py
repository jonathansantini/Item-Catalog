from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CategoryItem, User

engine = create_engine('sqlite:///categories.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(name="Tommy McTester", email="tommy@mctesters.com",
             picture='')
session.add(User1)
session.commit()

# First Category
category1 = Category(user_id="1", name="Albums")

session.add(category1)
session.commit()

categoryItem1 = CategoryItem(user_id="1", name="Ok Computer", description="OK Computer is the third studio album by English rock band Radiohead, released on 16 June 1997 on EMI subsidiaries Parlophone and Capitol Records. The members of Radiohead self-produced the album with Nigel Godrich, an arrangement they have used for their subsequent albums. Other than the song 'Lucky', recorded in 1995, Radiohead recorded OK Computer in Oxfordshire and Bath between 1996 and early 1997, mostly in the historic mansion St Catherine's Court. The band distanced themselves from the guitar-centred, lyrically introspective style of their previous album, The Bends. OK Computer's abstract lyrics, densely layered sound and eclectic influences laid the groundwork for Radiohead's later, more experimental work.",
                     category=category1)

session.add(categoryItem1)
session.commit()

# Second Category
category2 = Category(user_id="1", name="Books")

session.add(category2)
session.commit()

categoryItem1 = CategoryItem(user_id="1", name="One Hundred Years of Solitude", description="One Hundred Years of Solitude is a landmark 1967 novel by Colombian author Gabriel Garcia Marquez that tells the multi-generational story of the Buendia family, whose patriarch, Jose Arcadio Buendia, founded the town of Macondo, a fictitious town in the country of Colombia.",
                     category=category2)

session.add(categoryItem1)
session.commit()

# Third Category
category3 = Category(user_id="1", name="Video Games")

session.add(category3)
session.commit()

categoryItem1 = CategoryItem(user_id="1", name="Metal Gear Solid", description="Metal Gear Solid[a] is an action-adventure stealth video game developed by Konami Computer Entertainment Japan and released for the PlayStation in 1998. The game was directed, produced, and written by Hideo Kojima, and serves as a sequel to the MSX2 video games Metal Gear and Metal Gear 2: Solid Snake, which Kojima also worked on. The game was first unveiled in the Tokyo Game Show in 1996 and subsequently shown in the Electronic Entertainment Expo in 1997, before eventually releasing in late 1998.",
                     category=category3)

session.add(categoryItem1)
session.commit()

print("added category items!")
