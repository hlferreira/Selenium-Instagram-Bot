from selenium import webdriver
from time import sleep

class InstaBot:
    #login in to instagram
    def __init__(self,username,pw):
        self.username = username
        self.pw = pw
        self.friends = []
        self.driver = webdriver.Chrome()
        self.driver.get("https://instagram.com")
        sleep(2)
        try:
            self.driver.find_element_by_xpath("//a[contains(text(), 'Log in')]").click()
            sleep(2)
            login_field = self.driver.find_element_by_xpath("//input[@name =\"username\"]").send_keys(username)
            pw_field = self.driver.find_element_by_xpath("//input[@name =\"password\"]").send_keys(pw)
        except:
            login_field = self.driver.find_element_by_xpath("//input[@name =\"username\"]").send_keys(username)
            pw_field = self.driver.find_element_by_xpath("//input[@name =\"password\"]").send_keys(pw)

        self.driver.find_element_by_xpath('//button[@type="submit"]').click()
        sleep(4)
        self.driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()
    
    #returns the usrs followers
    def getFollowers(self, usr):
        try:
            self.driver.find_element_by_xpath("//a[@href= \"/" + usr + "/followers/\"" + "]").click()
        except:
            self.driver.get("https://instagram.com/" + usr)
            self.driver.find_element_by_xpath("//a[@href= \"/" + usr + "/followers/\"" + "]").click()

        sleep(1)
        #scrolls all the way down to have all users loaded
        scrollBox = self.driver.find_element_by_xpath('/html/body/div[4]/div/div[2]')
        lastHeight, sBheight = 0, 1 
        
        while(lastHeight != sBheight):
            lastHeight = sBheight
            sleep(1)
            sBheight = self.driver.execute_script("arguments[0].scrollTo(0,arguments[0].scrollHeight);return arguments[0].scrollHeight", scrollBox)
        
        links = scrollBox.find_elements_by_tag_name('a')
        followersNames = [name.text for name in links if name.text != '']
        self.driver.find_element_by_xpath("/html/body/div[4]/div/div[1]/div/div[2]/button").click()
        return followersNames
    
    #returns all the people the usrs follow
    def getFollowing(self, usr):
        try:
            self.driver.find_element_by_xpath("//a[@href= \"/" + usr + "/following/\"" + "]").click()
        except:
            self.driver.get("https://instagram.com/" + usr)
            try:
                self.driver.find_element_by_xpath("//a[@href= \"/" + usr + "/following/\"" + "]").click()
            except:
                return []
        sleep(1)
        #scrolls all the way down to have all users loaded
        scrollBox = self.driver.find_element_by_xpath('/html/body/div[4]/div/div[2]')
        lastHeight, sBheight = 0, 1 
        
        while(lastHeight != sBheight):
            lastHeight = sBheight
            sleep(1)
            sBheight = self.driver.execute_script("arguments[0].scrollTo(0,arguments[0].scrollHeight);return arguments[0].scrollHeight", scrollBox)
        
        links = scrollBox.find_elements_by_tag_name('a')
        followingNames = [name.text for name in links if name.text != '']
        self.driver.find_element_by_xpath("/html/body/div[4]/div/div[1]/div/div[2]/button").click()
        return followingNames

    #find the people that don't follow the usr but the usr follows
    def getUnfollowers(self, usr):
        self.driver.get("https://instagram.com/" + usr)
        sleep(2)

        followers = self.getFollowers(usr)
        following = self.getFollowing(usr)
        
        unfollowingList = [name for name in following if name not in followers and name != ""]
        print(len(unfollowingList))
        return print(unfollowingList)
    
    #friends are the people who follow and are followed by the user
    def getFriends(self, usr):
        self.driver.get("https://instagram.com/" + usr)
        sleep(2)          

        followers = self.getFollowers(usr)
        following = self.getFollowing(usr)

        friendsList = [name for name in following if name in followers and name != ""]
        return friendsList
    
    #find the people that follow the usr and the usr doens't follow - not really tested
    def getFansList(self, usr):
        self.driver.get("https://instagram.com/" + usr)
        sleep(2)

        followers = self.getFollowers(usr)
        following = self.getFollowing(usr)

        fanslist = [name for name in followers if name not in following and name != ""]
        print(len(fanslist))
        print(fanslist)
        return fanslist

    #find the people all usrs are followed by
    def commonFollowers(self, usrs):
        commonList = self.getFollowers(usrs[0])
        i=1
        for i in range(len(usrs)):
            followersList = self.getFollowers(usrs[i])
            commonList = [name for name in followersList if name in commonList and name != ""]
        print(len(commonList))
        print(commonList)

    #find the people all usrs follow
    def commonFollowing(self, usrs):
        commonList = self.getFollowing(usrs[0])
        i=1
        for i in range(len(usrs)):
            followingList = self.getFollowing(usrs[i])
            commonList = [name for name in followingList if name in commonList and name != ""]
        print(len(commonList))
        print(commonList)
    
    #find the people who the usrs follow and are followed by them in common between the users
    def commonFriends(self, usrs):
        if usrs[0] != self.username:
            commonList = self.getFriends(usrs[0])
        elif self.friends != []:
            commonList = self.friends
        else:
            self.friends = self.getFriends(self.username) 
            commonList = self.getFriends(self.username)
        i=1 
        for i in range(i, len(usrs)):
            friendsList = self.getFriends(usrs[i])
            commonList = [name for name in friendsList if name in commonList and name != ""]
        return [len(commonList), commonList]

    #make a json with the friends
    def makejsonfile(self, usr):
        self.friends = self.getFriends(usr)
        f = open("instagramFriendsNetwork.json", "w+")
        separator = "\", \""
        f.write("[\n\t{\n\t\"" + usr + "\" : {\n\t" + "\"friends\": [\"" + separator.join(self.friends) + "\"]\n\t}\n},")

        i = 0
        for i in range(len(self.friends)):
            commonFriendsLen, commonFriends = self.commonFriends([self.username, self.friends[i]])
            f.write("{\n\t\"" + self.friends[i] + "\" : {\n\t" + "\"followers\": [\"" + separator.join(commonFriends) + "\"]\n\t, \"commonNumber\": " + str(commonFriendsLen) +  "}\n},")
        
        f.write("\n\t}\n]")
        f.close()

    def makejsonforuser(self, usr):
        commonFriendsLen, commonFriends = self.checkusers(usr)
        f = open("instagramFriendsNetwork.json", "a")
        separator = "\", \""
        f.write("{\n\t\"" + usr + "\" : {\n\t" + "\"followers\": [\"" + separator.join(commonFriends) + "\"]\n\t, \"commonNumber\": " + str(commonFriendsLen) +  "}\n},")
        f.close()

    #not interesting - improved version of commonfriends
    def checkusers(self, usr):
        self.driver.get("https://instagram.com/" + usr)
        sleep(2)
        
        #Uses the "in common button"
        try:
            a = self.driver.find_element_by_xpath("//span[contains(text(), 'Followed by')]") 
            text = mybot.driver.execute_script('return arguments[0].innerText;', a)
            number = int(text[text.index("+") + 2 : text.index("more")-1])

            self.driver.find_element_by_xpath("//a[@href = \"/" + usr + "/followers/mutualOnly\"" + "]").click()
            sleep(1)
            self.driver.find_element_by_xpath("//a[@href = \"/" + usr + "/followers/mutualFirst\"" + "]").click()

            followB = self.driver.find_element_by_xpath("//button[contains(text(), 'Follow')]")
            self.driver.execute_script('arguments[0].scrollIntoView()', followB)

            scrollBox = self.driver.find_element_by_xpath('/html/body/div[4]/div/div[2]')
            links = scrollBox.find_elements_by_tag_name('a')

            followersNames = [name.text for name in links if name.text != '']
            
            followersNames = followersNames[:number+3]
            self.driver.find_element_by_xpath("/html/body/div[4]/div/div[1]/div/div[2]/button").click()
        except:
            #When the user has less then 4 common following, if for each case 1, 2 or 3
            try:
                a = self.driver.find_element_by_xpath("//span[contains(text(), 'Followed by')]") 
                text = mybot.driver.execute_script('return arguments[0].innerText;', a)
            except:
                text = ''
            followersNames = []

            if ',' in text:
                followersNames.append(text[text.index('by ') + 3:text.index(',')])
                print(text[text.index('by ') + 3:text.index(',')])
                text = text[text.index(',') + 2:]
            elif 'and' in text:
                followersNames.append(text[text.index('by ') + 3:text.index(' and')])
                text = text[text.index(' and') + 5:]
            else:
                followersNames.append(text[text.index('by ') + 3:])

            if ',' in text:
                followersNames.append(text[:text.index(',')])
                text = text[text.index(',') + 6:]
                followersNames.append(text)
            elif text != '':
                followersNames.append(text)
            print(followersNames)

        followers = self.getFollowing(usr)

        if self.friends == []:
            self.friends = self.getFriends(self.username)
        
        mutualFollowers = [name for name in followersNames if name in followers]

        mutualFriends = [name for name in mutualFollowers if name in self.friends]

        return [len(mutualFriends), mutualFriends]

    #spam likes in the use
    def likePhotos(self, usr, sleepTime):
        sleep(sleepTime)
        self.driver.get("https://instagram.com/" + usr)
        sleep(2)

        photos = self.driver.find_elements_by_class_name("_9AhH0")
        photosPassed = []

        i = 0
        while i < len(photos) -1 :
            photos[i].click()
            
            photosPassed.append(photos[i])
            lastPhoto = photos[i]
            sleep(1)

            likeButton = mybot.driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/div[2]/section[1]/span[1]/button')
            
            svg = likeButton.find_element_by_tag_name("svg")
            
            #Like means the user doens't like the photo
            if mybot.driver.execute_script("return arguments[0].getAttribute('aria-label')", svg) == "Like" :
                likeButton = mybot.driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/div[2]/section[1]/span[1]/button').click()
        
            #scrolls the photo into view to load new photos
            mybot.driver.execute_script('arguments[0].scrollIntoView()', photos[i])

            #class for the photos
            photos_aux = self.driver.find_elements_by_class_name("_9AhH0")
            try:
                #when you go down on the user's page the last photos will "unload"
                i = photos_aux.index(lastPhoto) + 1
            except:
                print('error :' + str(i))
            photos = photos_aux

            self.driver.find_element_by_xpath('/html/body/div[4]/button[1]').click()

        return photosPassed
                



            

mybot = InstaBot('username', 'password')
