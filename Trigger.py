# coding=utf-8

import utility
from mcpi.block import *
from mcpi.vec3 import *
from time import *

#################################################
#         Base classes for all triggers         #
#################################################

class TriggerStepOn(object):
    """Base class for blocks that trigger an event when it is step on"""

    def __init__(self, x, y, z, block_type, block_data=0, one_time=True):
        # set values
        self.pos = Vec3(x, y + 1, z)
        self.block = Block(block_type, block_data)
        self.one_time = one_time

        # add self to triggers list
        utility.triggers.append(self)

        # set block under trigger block to correct type
        utility.mc.setBlock(x, y, z, self.block)

    def condition(self):
        """check if hansel steps on block"""
        if self.pos == utility.tilePos:
            return True
        return False

    def action(self):
        pass


class TriggerComeClose(object):
    """Base class for blocks that trigger an event when hansel is close enough"""

    def __init__(self, x, y, z, d, block_type, block_data=0, one_time=True):
        # set values
        self.pos = Vec3(x, y, z)
        self.block = Block(block_type, block_data)
        self.one_time = one_time
        self.d = d

        # add self to triggers list
        utility.triggers.append(self)

    def distance(self):
        return (self.pos - utility.pos).length()

    def condition(self):
        """check if hansel is close enough"""
        if self.distance() < self.d:
            return True
        return False

    def action(self):
        pass


#################################################
#                    Messages                   #
#################################################

class Message(TriggerComeClose):
    """Base class for showing message to player"""

    def __init__(self, x, y, z, message, d=2, block_type=0, block_data=0, one_time=True):
        TriggerComeClose.__init__(self, x, y, z, d, block_type, block_data, one_time)
        self.message = message

    def action(self):
        utility.mc.postToChat(self.message)


################################################
#              Traps in the maze               #
################################################

# -------------------Falling------------------ #
class FallTrap(TriggerStepOn):
    def __init__(self, x, y, z, depth, block_type, block_data=0, one_time=True):
        TriggerStepOn.__init__(self, x, y, z, block_type, block_data, one_time)
        self.depth = self.pos.y - depth

        # create a hole
        utility.mc.setBlocks(self.pos.x, self.pos.y - 2, self.pos.z,
                             self.pos.x, self.depth, self.pos.z, AIR)

    def action(self):
        utility.mc.setBlock(utility.tilePos.x, utility.tilePos.y - 1, utility.tilePos.z, AIR)


class FallIntoMazeTrap(FallTrap):
    """This will open a hole under Hansel and he 
    will fall into the lowest level of the maze"""

    def __init__(self, x, y, z):
        FallTrap.__init__(self, x, y, z, 10 * utility.number_of_floor, STONE.id, 0, True)

        # create a chamber at the end of the hole
        utility.mc.setBlocks(utility.pos.x - 5, self.depth, utility.pos.z - 5,
                             utility.pos.x + 5, self.depth - 5, utility.pos.z + 5, AIR)

        # create water in the chamber to catch hansel
        utility.mc.setBlocks(utility.pos.x - 5, self.depth - 5, utility.pos.z - 5,
                             utility.pos.x + 5, self.depth - 10, utility.pos.z + 5, WATER)


class FallIntoLavaTrap(FallTrap):
    def __init__(self, x, y, z):
        FallTrap.__init__(self, x, y, z, 3, STONE.id, 0, True)
        utility.mc.setBlock(x, self.depth, z, LAVA)


class PushBackTrap(TriggerComeClose):
    def __init__(self, x, y, z, d):
        TriggerComeClose.__init__(self, x, y, z, d, STONE.id, 0, False)

    def movePlayer(self, vec3):
        newPos = vec3 + utility.pos
        utility.hansel.setPos(newPos.x, newPos.y, newPos.z)

    def action(self):
        if self.distance() > d / 3:
            self.oldPos = utility.pos
        else:
            step = self.oldPos - utility.pos
            for i in xrange(20):
                self.movePlayer(step)
                sleep(0.1)


class FlowLavaBlockWay_x(TriggerStepOn):
    """
    block both directions w/ lava(change x)
    """
    def __init__(self, x, y, z):
        TriggerStepOn.__init__(self, x, y, z, STONE.id, 0, True)

    def action(self):
        x = utility.pos.x
        y = utility.pos.y
        z = utility.pos.z
        utility.mc.setBlock(x + 5, y, z, LAVA)
        utility.mc.setBlock(x + 6, y, z, STONE)
        utility.mc.setBlock(x - 5, y, z, LAVA)
        utility.mc.setBlock(x - 6, y, z, STONE)


class FlowLavaBlockWay_z(TriggerStepOn):
    """
    block both directions w/ lava(change z)
    """
    def __init__(self, x, y, z):
        TriggerStepOn.__init__(self, x, y, z, STONE.id, 0, True)

    def action(self):
        x = utility.pos.x
        y = utility.pos.y
        z = utility.pos.z
        utility.mc.setBlock(x, y, z + 5, LAVA)
        utility.mc.setBlock(x, y, z + 6, STONE)
        utility.mc.setBlock(x, y, z - 5, LAVA)
        utility.mc.setBlock(x, y, z - 6, STONE)


class StoneBlockWay_x(TriggerStepOn):
    """
    block ways w/ rising blocks (change x)
    """
    def __init__(self, x, y, z):
        TriggerStepOn.__init__(self ,x, y, z, STONE.id, 0, True)

    def action(self):
        x = utility.pos.x
        y = utility.pos.y
        z = utility.pos.z
        for i in xrange(4):
            utility.mc.setBlock(x + 5, y, z, STONE_BRICK)
            utility.mc.setBlock(x - 5, y, z, STONE_BRICK)
            y += 1
            sleep(2)


class StoneBlockWay_z(TriggerStepOn):
    """
    block ways w/ rising blocks (change z)
    """
    def __init__(self, x, y, z):
        TriggerStepOn.__init__(self, x, y, z, STONE.id, 0, True)

    def action(self):
        x = utility.pos.x
        y = utility.pos.y
        z = utility.pos.z
        for i in xrange(4):
            utility.mc.setBlock(x, y, z + 3, STONE_BRICK)
            utility.mc.setBlock(x, y, z - 3, STONE_BRICK)
            y += 1
            sleep(3)


class FallSand(TriggerStepOn):
    """
    sand fall on ur head
    """
    def __init__(self, x, y, z):
        TriggerStepOn.__init__(self, x, y, z, STONE.id, 0, True)

    def action(self):
        utility.mc.setBlock(utility.pos.x, utility.pos.y + 3, utility.pos.z, SAND)


class TrapInHole_x(TriggerStepOn):
    """
    trap you in a hole with closing door (change x)
    """
    def __init__(self, x, y, z):
        TriggerStepOn.__init__(self, x, y, z, STONE.id, 0, True)

    def action(self):
        x = utility.pos.x
        y = utility.pos.y
        z = utility.pos.z
        utility.mc.setBlocks(x, y - 1, z, x + 5, y - 3, z, AIR)
        sleep(3)
        for i in xrange(6):
            utility.mc.setBlock(x, y - 1, z, 89)
            x += 1
            sleep(1)


class TrapInHole_z(TriggerStepOn):
    """
    trap you in a hole with closing door (change x)
    """
    def __init__(self, x, y, z):
        TriggerStepOn.__init__(self, x, y, z, STONE.id, 0, True)

    def action(self):
        x = utility.pos.x
        y = utility.pos.y
        z = utility.pos.z
        utility.mc.setBlocks(x, y - 1, z, x, y - 3, z + 5, AIR)
        sleep(3)
        for i in xrange(6):
            utility.mc.setBlock(x, y - 1, z, 89)
            z += 1
            sleep(1)



################################################
#                 Final trap                   #
################################################
